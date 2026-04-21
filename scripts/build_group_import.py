#!/usr/bin/env python3
"""Build a StudyDesk group import CSV from a team-registration spreadsheet."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


TEAM_ID_RE = re.compile(r"(\d+)")
MEMBER_NAME_RE = re.compile(r"member\s+(\d+)\s+full\s+name", re.IGNORECASE)
MEMBER_EMAIL_RE = re.compile(r"member\s+(\d+)\s+(?:usq\s+)?email", re.IGNORECASE)
MEMBER_CONSENT_RE = re.compile(r"member\s+(\d+)\s+consent", re.IGNORECASE)
IDNUMBER_RE = re.compile(r"(?:^|[^0-9])u?(\d{7})(?:[^0-9]|$)", re.IGNORECASE)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def normalize_email(value: str) -> str:
    return normalize(value)


def extract_team_id(raw_value: str) -> str | None:
    match = TEAM_ID_RE.search((raw_value or "").strip())
    return match.group(1) if match else None


def extract_idnumber(email_or_text: str) -> str | None:
    match = IDNUMBER_RE.search((email_or_text or "").strip())
    if not match:
        return None
    return f"006{match.group(1)}"


@dataclass
class MemberRow:
    team_id: str
    groupname: str
    member_slot: int
    member_name: str
    source_email: str
    idnumber: str
    consent: str


def read_sheet_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def find_header_row(rows: list[list[str]]) -> int:
    for index, row in enumerate(rows):
        normalized = [normalize(cell) for cell in row]
        if "team id" in normalized and any(MEMBER_NAME_RE.fullmatch(cell) for cell in normalized):
            return index
    raise ValueError("Could not find a header row containing 'Team ID' and member columns.")


def build_header_maps(headers: list[str]) -> tuple[int, dict[int, int], dict[int, int], dict[int, int]]:
    team_column = None
    name_columns: dict[int, int] = {}
    email_columns: dict[int, int] = {}
    consent_columns: dict[int, int] = {}

    for index, header in enumerate(headers):
        normalized_header = normalize(header)
        if normalized_header == "team id":
            team_column = index
            continue

        name_match = MEMBER_NAME_RE.fullmatch(normalized_header)
        if name_match:
            name_columns[int(name_match.group(1))] = index
            continue

        email_match = MEMBER_EMAIL_RE.fullmatch(normalized_header)
        if email_match:
            email_columns[int(email_match.group(1))] = index
            continue

        consent_match = MEMBER_CONSENT_RE.fullmatch(normalized_header)
        if consent_match:
            consent_columns[int(consent_match.group(1))] = index

    if team_column is None:
        raise ValueError("Missing 'Team ID' column.")

    member_slots = sorted(set(name_columns) | set(email_columns))
    incomplete = [slot for slot in member_slots if slot not in name_columns or slot not in email_columns]
    if incomplete:
        raise ValueError(f"Member columns are incomplete for slot(s): {', '.join(map(str, incomplete))}")

    return team_column, name_columns, email_columns, consent_columns


def load_overrides(path: Path | None) -> tuple[dict[tuple[str, str], str], dict[tuple[str, str], str], dict[str, str], dict[str, str]]:
    by_team_name: dict[tuple[str, str], str] = {}
    by_team_email: dict[tuple[str, str], str] = {}
    by_name: dict[str, str] = {}
    by_email: dict[str, str] = {}

    if path is None:
        return by_team_name, by_team_email, by_name, by_email

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"idnumber"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Override CSV is missing required column(s): {', '.join(sorted(missing))}")

        for row in reader:
            idnumber = (row.get("idnumber") or "").strip()
            if not idnumber:
                continue

            team_id = (row.get("team_id") or "").strip()
            member_name = normalize(row.get("member_name") or "")
            source_email = normalize_email(row.get("source_email") or "")

            # Treat each row as one explicit matching rule.
            # Do not also populate broader fallbacks from the same row, otherwise a
            # duplicate typo email can accidentally override multiple students.
            if team_id and member_name:
                by_team_name[(team_id, member_name)] = idnumber
            elif team_id and source_email:
                by_team_email[(team_id, source_email)] = idnumber
            elif member_name:
                by_name[member_name] = idnumber
            elif source_email:
                by_email[source_email] = idnumber

    return by_team_name, by_team_email, by_name, by_email


def resolve_idnumber(
    team_id: str,
    member_name: str,
    source_email: str,
    overrides: tuple[dict[tuple[str, str], str], dict[tuple[str, str], str], dict[str, str], dict[str, str]],
) -> tuple[str | None, str | None]:
    by_team_name, by_team_email, by_name, by_email = overrides
    normalized_name = normalize(member_name)
    normalized_email = normalize_email(source_email)

    if (team_id, normalized_name) in by_team_name:
        return by_team_name[(team_id, normalized_name)], "team_id + member_name"
    if (team_id, normalized_email) in by_team_email:
        return by_team_email[(team_id, normalized_email)], "team_id + source_email"
    if normalized_name in by_name:
        return by_name[normalized_name], "member_name"
    if normalized_email in by_email:
        return by_email[normalized_email], "source_email"

    return extract_idnumber(source_email), None


def write_csv(path: Path, rows: list[MemberRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["idnumber", "groupname"])
        for row in rows:
            writer.writerow([row.idnumber, row.groupname])


def write_issues(
    path: Path,
    source: Path,
    rows: list[MemberRow],
    warnings: list[str],
    blocking: list[str],
    overrides_applied: list[str],
    skipped_teams: list[str],
    header_row_number: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    group_sizes: dict[str, int] = defaultdict(int)
    for row in rows:
        group_sizes[row.groupname] += 1

    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"Source: {source}\n")
        handle.write(f"Header row: {header_row_number}\n")
        handle.write(f"Members parsed: {len(rows)}\n")
        handle.write(f"Groups parsed: {len(group_sizes)}\n")
        if skipped_teams:
            handle.write(f"Skipped team IDs: {', '.join(skipped_teams)}\n")
        if group_sizes:
            handle.write("Group sizes:\n")
            for groupname in sorted(group_sizes, key=lambda value: int(value)):
                handle.write(f"  {groupname}: {group_sizes[groupname]}\n")

        if overrides_applied:
            handle.write("Overrides applied:\n")
            for item in overrides_applied:
                handle.write(f"  - {item}\n")

        if warnings:
            handle.write("Warnings:\n")
            for item in warnings:
                handle.write(f"  - {item}\n")

        if blocking:
            handle.write("Blocking issues:\n")
            for item in blocking:
                handle.write(f"  - {item}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="CSV export of the team registration sheet.")
    parser.add_argument("--output", type=Path, help="Destination CSV for StudyDesk import.")
    parser.add_argument("--issues", type=Path, help="Destination text report.")
    parser.add_argument("--overrides", type=Path, help="Optional CSV of manual idnumber corrections.")
    parser.add_argument(
        "--exclude-team",
        action="append",
        default=["0"],
        help="Team ID to skip. Repeat for multiple values. Defaults to 0.",
    )
    parser.add_argument(
        "--groupname-template",
        default="{team_id}",
        help="Python format string for output group names. Available field: team_id.",
    )
    args = parser.parse_args()

    rows = read_sheet_rows(args.source)
    header_index = find_header_row(rows)
    headers = rows[header_index]
    team_column, name_columns, email_columns, consent_columns = build_header_maps(headers)
    overrides = load_overrides(args.overrides)

    parsed_rows: list[MemberRow] = []
    warnings: list[str] = []
    blocking: list[str] = []
    overrides_applied: list[str] = []
    skipped_teams: list[str] = []
    excluded_teams = {str(value) for value in args.exclude_team}

    for raw_row in rows[header_index + 1 :]:
        if not any((cell or "").strip() for cell in raw_row):
            continue

        padded = raw_row + [""] * (len(headers) - len(raw_row))
        team_id = extract_team_id(padded[team_column])
        if not team_id:
            continue
        if team_id in excluded_teams:
            skipped_teams.append(team_id)
            continue

        groupname = args.groupname_template.format(team_id=team_id)

        for slot in sorted(name_columns):
            member_name = (padded[name_columns[slot]] or "").strip()
            source_email = (padded[email_columns[slot]] or "").strip()
            consent = (padded[consent_columns[slot]] or "").strip() if slot in consent_columns else ""

            if not member_name and not source_email:
                continue
            if not member_name or not source_email:
                blocking.append(
                    f"Team {team_id} member slot {slot} is incomplete: name={member_name!r}, email={source_email!r}"
                )
                continue

            idnumber, override_source = resolve_idnumber(team_id, member_name, source_email, overrides)
            if not idnumber:
                blocking.append(f"Team {team_id} {member_name}: could not derive idnumber from {source_email!r}")
                continue
            if not re.fullmatch(r"\d{10}", idnumber):
                blocking.append(f"Team {team_id} {member_name}: invalid idnumber {idnumber!r}")
                continue

            if override_source:
                overrides_applied.append(
                    f"Team {team_id} {member_name} -> {idnumber} via override ({override_source})"
                )

            if consent and normalize(consent) != "yes":
                warnings.append(f"Team {team_id} {member_name}: consent is {consent!r}, not 'YES'")
            if not consent:
                warnings.append(f"Team {team_id} {member_name}: consent is blank")

            parsed_rows.append(
                MemberRow(
                    team_id=team_id,
                    groupname=groupname,
                    member_slot=slot,
                    member_name=member_name,
                    source_email=source_email,
                    idnumber=idnumber,
                    consent=consent,
                )
            )

    id_counter = Counter(row.idnumber for row in parsed_rows)
    duplicates = sorted(idnumber for idnumber, count in id_counter.items() if count > 1)
    for idnumber in duplicates:
        members = [f"team {row.team_id} {row.member_name}" for row in parsed_rows if row.idnumber == idnumber]
        blocking.append(f"Duplicate idnumber {idnumber}: {', '.join(members)}")

    parsed_rows.sort(key=lambda row: (int(row.team_id), row.member_slot))

    if args.issues:
        write_issues(
            args.issues,
            args.source,
            parsed_rows,
            warnings,
            blocking,
            overrides_applied,
            skipped_teams,
            header_index + 1,
        )

    if blocking:
        if args.output and args.output.exists():
            args.output.unlink()
        for item in blocking:
            print(f"[ERROR] {item}", file=sys.stderr)
        if args.issues:
            print(f"[INFO] Wrote issues report to {args.issues}", file=sys.stderr)
        return 1

    if args.output:
        write_csv(args.output, parsed_rows)
        print(f"[OK] Wrote import CSV to {args.output}")
    if args.issues:
        print(f"[OK] Wrote issues report to {args.issues}")

    group_sizes = Counter(row.groupname for row in parsed_rows)
    print(f"[OK] Parsed {len(parsed_rows)} members across {len(group_sizes)} groups")
    for groupname in sorted(group_sizes, key=lambda value: int(value)):
        print(f"  - group {groupname}: {group_sizes[groupname]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

---
name: studydesk-group-import
description: Prepare, import, verify, and maintain StudyDesk/Moodle project groups from a team registration spreadsheet. Use when Codex needs to convert a CSV team registration form into `idnumber,groupname` import data, import members through the StudyDesk group-member import page, verify group counts in the browser, diagnose assignment warnings such as "Require group to make submission", or add or remove students after late changes, withdrawals, or team corrections.
---

# Studydesk Group Import

## Overview

Prepare a clean StudyDesk group import from a spreadsheet first, then perform the browser import and verification. Prefer `idnumber` imports over username or email imports because preview errors are easier to diagnose and the mapping is more stable.

## Workflow

1. Inspect the source spreadsheet and confirm the user intent.
   Skip obvious example rows such as `Team ID 0` unless the user explicitly says otherwise.
   Treat late removals, solo-group requests, or assignment-access implications as decisions worth surfacing before making irreversible changes.

2. Build the import CSV before touching StudyDesk.
   Run `scripts/build_group_import.py` against the CSV export of the team registration sheet.
   If the source is `.xlsx`, export it to CSV first or use spreadsheet tooling to create an equivalent CSV.

3. Review the issues report.
   Stop if the script reports blocking issues such as duplicate `idnumber` values, missing student identifiers, incomplete member records, or malformed team IDs.
   Use an overrides CSV when the sheet contains typos or copied emails that point to the wrong student.
   See [references/troubleshooting.md](references/troubleshooting.md) for override format and common failure modes.

4. Import in StudyDesk with preview first.
   Open `Users > Groups > Import group members`.
   Upload the generated CSV with columns `idnumber,groupname`.
   Click `Preview` and read the entire preview result before importing.
   Only click `Import` when there are no lookup errors.

5. Verify the imported groups in the browser.
   Open `Users > Groups`.
   Confirm the expected numeric groups exist and the member counts match the spreadsheet.
   Spot-check any students that needed overrides or manual corrections.

6. Handle one-off changes after import.
   Use `Add/remove users` from the target group for withdrawals or manual corrections.
   Re-check the final group count after each change.
   If the user asks to exclude a student from group submission, explain that leaving them outside all target groups can keep the assignment warning active and block their submission path.

## Recommended Commands

Generate an issues report only:

```bash
python3 scripts/build_group_import.py \
  --source "/path/to/team-registration.csv" \
  --issues "/tmp/group-import-issues.txt"
```

Generate a clean import CSV plus issues report:

```bash
python3 scripts/build_group_import.py \
  --source "/path/to/team-registration.csv" \
  --output "/tmp/studydesk-group-import.csv" \
  --issues "/tmp/group-import-issues.txt" \
  --overrides "/path/to/overrides.csv"
```

## Browser Notes

- Prefer the direct group-member import workflow over manual per-student edits when many groups are involved.
- Use the Computer Use plugin when the user wants the live StudyDesk site updated in the browser.
- If the user provides a Panopto or written guide, use it to confirm terminology or UI labels, but do not ignore a faster built-in import path that is already available in StudyDesk.

## Assignment Warning Triage

The warning about `Require group to make submission` does not automatically mean a student is duplicated across two project groups.

Check these cases in order:

1. A student is in zero groups within the assignment's target grouping.
2. A student is in more than one group within that target grouping.
3. The course contains unrelated tutorial, online, or staff groups that make the UI show `(2)` or `(3)` next to a person.

The `(2)` or `(3)` count in `Add/remove users` reflects total course-group memberships, not necessarily duplicate memberships inside the assignment's project grouping.

See [references/troubleshooting.md](references/troubleshooting.md) for a deeper checklist.

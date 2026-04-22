# StudyDesk Group Import Pack

Shareable pack for preparing and importing project groups into StudyDesk/Moodle from a team-registration spreadsheet.

This pack is designed for mixed-tool teams:

- Codex users can install the native Codex skill.
- Claude Code users can use the included prompt plus the shared Python script.
- Cursor users can use the same script and prompt-based workflow.

## What this pack includes

- `scripts/build_group_import.py`
  Build a clean `idnumber,groupname` import CSV from a team-registration CSV.
- `docs/workflow.md`
  Human-readable workflow for preparation, import, verification, and warning triage.
- `docs/troubleshooting.md`
  Common StudyDesk/Moodle problems and override rules.
- `examples/overrides.example.csv`
  Example manual correction file for typoed emails or copied student IDs.
- `prompts/`
  Ready-to-paste prompts for Codex, Claude Code, and Cursor.
- `codex-skill/studydesk-group-import/`
  Native Codex skill folder for users who want proper skill installation.

## Best way to share it

The best option is to put this whole folder in an internal Git repository or shared project folder.

Recommended sharing methods:

1. Internal Git repo
   Best for versioning, fixes, and team reuse.
2. Shared OneDrive / SharePoint folder
   Good if your team is less Git-heavy.
3. Zip archive
   Fine for one-off sharing, but harder to update later.

If several people will use it more than once, prefer the Git-repo route.

## Quick start

### 1. Prepare the import CSV

Run:

```bash
python3 scripts/build_group_import.py \
  --source "/path/to/team-registration.csv" \
  --output "/path/to/studydesk-group-import.csv" \
  --issues "/path/to/studydesk-group-import-issues.txt"
```

If the source spreadsheet contains typoed emails or copied student IDs, add an override file:

```bash
python3 scripts/build_group_import.py \
  --source "/path/to/team-registration.csv" \
  --overrides "examples/overrides.example.csv" \
  --output "/path/to/studydesk-group-import.csv" \
  --issues "/path/to/studydesk-group-import-issues.txt"
```

### 2. Import in StudyDesk

Use:

- `Users > Groups > Import group members`

Upload the generated CSV and always run `Preview` before `Import`.

### 3. Verify

Check:

- expected group count
- expected member count per group
- any manually corrected students

See [docs/workflow.md](docs/workflow.md) for the full checklist.

## For Codex users

Install the native skill by copying the folder:

- from: `codex-skill/studydesk-group-import`
- to: `~/.codex/skills/studydesk-group-import`

Then use a prompt like:

```text
Use $studydesk-group-import to prepare and verify a StudyDesk group import from this team-registration CSV, exclude Team ID 0, generate an issues report, and help me complete the browser import safely.
```

If the user does not want to install the skill, they can still use the script and the prompt file at [prompts/codex.md](prompts/codex.md).

## For Claude Code users

Claude Code does not use the Codex skill format directly, so the simplest workflow is:

1. Open this folder in the working directory.
2. Ask Claude Code to read:
   - `README.md`
   - `docs/workflow.md`
   - `docs/troubleshooting.md`
3. Ask it to run `scripts/build_group_import.py`.
4. Use the prompt at [prompts/claude-code.md](prompts/claude-code.md).

## For Cursor users

Cursor users can use the same portable workflow as Claude Code users:

1. Open this folder or repo in Cursor.
2. Point the agent to:
   - `README.md`
   - `docs/workflow.md`
   - `docs/troubleshooting.md`
3. Ask it to run `scripts/build_group_import.py`.
4. Start with the prompt at [prompts/cursor.md](prompts/cursor.md).

## Notes for browser automation

The script is cross-tool and does not depend on browser automation.

Live StudyDesk actions such as:

- importing groups
- previewing the CSV
- removing a student from a group
- checking assignment warnings

depend on whether the agent/tool has browser-control capability in the current environment.

If browser control is unavailable, the tool can still:

- build the import file
- detect duplicates and likely sheet errors
- produce an issues report
- give a precise manual checklist for StudyDesk

## Language

This pack is written in English on purpose so it is easier to hand over to colleagues.

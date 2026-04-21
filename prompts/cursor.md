Use the StudyDesk Group Import Pack in this workspace.

Start by reading:

- `README.md`
- `docs/workflow.md`
- `docs/troubleshooting.md`

Next:

1. Run `scripts/build_group_import.py` on the provided team-registration CSV.
2. Exclude `Team ID 0` unless I explicitly say to keep it.
3. Generate:
   - a clean `idnumber,groupname` CSV for StudyDesk
   - an issues report
4. If the source spreadsheet is dirty, create or recommend an override CSV rather than silently patching the source data.
5. If browser tools are available, help me complete:
   - `Users > Groups > Import group members`
   - preview
   - import
   - final verification
6. If browser tools are not available, give me a precise manual checklist.
7. If StudyDesk shows a group-submission warning, determine whether the real problem is:
   - no relevant project group for a student, or
   - more than one relevant project group
   and do not confuse that with unrelated tutorial or online groups in the course.

Prefer safe, auditable steps and call out anything that could affect live student groups.

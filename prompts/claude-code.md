Use the StudyDesk Group Import Pack in this workspace.

Read these files first:

- `README.md`
- `docs/workflow.md`
- `docs/troubleshooting.md`

Then do the following:

1. Run `scripts/build_group_import.py` on the provided team-registration CSV.
2. Exclude `Team ID 0` unless I explicitly tell you otherwise.
3. Produce:
   - a clean StudyDesk import CSV with columns `idnumber,groupname`
   - an issues report
4. If the spreadsheet contains copied or typoed emails, create or suggest an override CSV instead of silently guessing.
5. Tell me whether the source file contains:
   - duplicate student IDs
   - incomplete member rows
   - invalid identifiers
   - blank consent values
6. If browser automation is available in this environment, help me import and verify the groups in StudyDesk.
7. If browser automation is not available, give me an exact manual checklist for the import and verification steps.
8. If the assignment page shows a group-submission warning, help me determine whether the cause is:
   - a student in no project group, or
   - a student in multiple project groups
   rather than assuming the issue is a duplicate import.

Be conservative with live course changes and explain any risky assumption before taking action.

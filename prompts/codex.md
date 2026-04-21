Use the StudyDesk Group Import Pack in this workspace.

Tasks:

1. Read `README.md`, `docs/workflow.md`, and `docs/troubleshooting.md`.
2. If native Codex skill installation is available, prefer the skill at `codex-skill/studydesk-group-import`.
3. Run `scripts/build_group_import.py` on the provided team-registration CSV.
4. Exclude `Team ID 0` unless I explicitly tell you not to.
5. Generate:
   - a clean `idnumber,groupname` import CSV
   - an issues report
6. If the source sheet has copied or typoed emails, propose or apply an override CSV instead of silently guessing.
7. If browser control is available, help me complete the StudyDesk import through `Users > Groups > Import group members`, preview the import, and verify the final groups.
8. If an assignment warning appears, determine whether the problem is:
   - a student in no relevant group, or
   - a student in more than one relevant group
   and do not assume course-wide group counts mean duplicate project-group membership.

Be explicit about assumptions and stop before risky changes if the next action could affect live student groups in a non-obvious way.

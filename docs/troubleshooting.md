# Troubleshooting

## Override CSV format

Use a CSV with these columns:

```csv
team_id,member_name,source_email,idnumber
2,mark atkinson,U1178862@umail.usq.edu.au,0061178376
20,Sabin Pandey,U1037606@umail.usq.edu.au,0061172795
```

Matching priority is:

1. `team_id + member_name`
2. `team_id + source_email`
3. `member_name`
4. `source_email`

Use `idnumber` in the normal 10-digit UniSQ format such as `0061178376`.

## Common import problems

### Preview says "No user exists ..."

Use `idnumber,groupname` instead of importing by username or free-form email. Regenerate the file with `scripts/build_group_import.py`.

### Source sheet contains the wrong email for a student

Add an override row instead of editing the original spreadsheet export in place. This keeps the correction explicit and reusable.

### Example row should not be imported

The builder excludes `Team ID 0` by default because many course registration sheets use it as a worked example row.

## Assignment warning: "Require group to make submission"

This warning usually means at least one user is:

1. Not in any group inside the assignment's target grouping, or
2. In more than one group inside that target grouping

Do not infer the cause from the warning alone.

Check:

1. The assignment grading summary for the target grouping name.
2. `Users > Groups` for the relevant project groups.
3. `Add/remove users` for any recently removed or corrected students.

## Interpreting `(2)` or `(3)` beside a student

In StudyDesk group editor views, that count reflects how many total course groups the person belongs to across the course. It does not prove they are duplicated across two project groups.

Tutorial, online, or staff groups can increase the count without breaking assignment submissions.

# Workflow

## Goal

Convert a team-registration spreadsheet into a safe StudyDesk/Moodle group import, then verify the imported groups and diagnose assignment-access problems if needed.

## Standard workflow

### 1. Export the registration sheet to CSV

Use a CSV export of the spreadsheet. The builder expects a header row with fields such as:

- `Team ID`
- `Member 1 Full Name`
- `Member 1 USQ email`
- `Member 1 consent`

and equivalent columns for Member 2 and Member 3.

### 2. Build the import file before touching StudyDesk

Run:

```bash
python3 scripts/build_group_import.py \
  --source "/path/to/team-registration.csv" \
  --output "/path/to/studydesk-group-import.csv" \
  --issues "/path/to/studydesk-group-import-issues.txt"
```

Default behavior:

- excludes `Team ID 0`
- derives `idnumber` from the email field
- stops on duplicate or invalid student IDs
- writes an issues report

### 3. Review the issues report

Do not import until blocking issues are resolved.

Typical blocking issues:

- duplicate student ID across rows
- malformed or missing email / identifier
- partial member row
- copied wrong email from another student

Typical warnings:

- missing consent
- consent not equal to `YES`

### 4. Apply overrides if the spreadsheet contains errors

Create an override CSV when the source file is wrong but you do not want to rewrite the original export.

Example:

```csv
team_id,member_name,source_email,idnumber
2,mark atkinson,U1178862@umail.usq.edu.au,0061178376
20,Sabin Pandey,U1037606@umail.usq.edu.au,0061172795
```

Then rerun the builder with `--overrides`.

### 5. Import in StudyDesk

Go to:

- `Users > Groups > Import group members`

Upload the generated CSV and click `Preview`.

Only proceed to `Import` when the preview shows no user-lookup errors.

### 6. Verify the result

Go to:

- `Users > Groups`

Check:

- all expected project groups exist
- each group has the expected number of students
- any corrected students are in the intended group

### 7. Handle late changes carefully

If a student is withdrawn, excluded, or moved after import:

1. open the target group
2. use `Add/remove users`
3. remove or move the student
4. re-check final counts

## Assignment warning triage

If the assignment page shows:

`Require group to make submission`

possible causes include:

1. a student is in zero groups inside the assignment's target grouping
2. a student is in more than one group inside the assignment's target grouping

Do not assume the warning automatically means a duplicate import.

Counts such as `(2)` or `(3)` beside a student often reflect tutorial, online, or staff groups elsewhere in the course.

Use the group editor and assignment grouping together to identify the true cause.

# tempo-utils
Utilities to help manage time entry in Tempo Timesheets

`tempo-copy-worklog` will copy the worklog entries from one week to the next

## Quick Usage Instructions

### Set environment variables

```bash
export TEMPO_API_TOKEN=<your Tempo API token>
export export JIRA_USER_ACCOUNT_ID=<your Jira user account id>
```

### Perform a dry run first

The following command will do a **dry run** of a copy of all of the worklogs for the timesheet for the week of March 23, 2025 into the timesheet for the week of March 30, 2025.

```bash
python tempo-copy-worklog.py --source 2025-03-23 --dest 2025-03-30 --dry-run
```

### Run it for real

Simply remove the `dry-run` flag to run it for real. 🚀

```bash
python tempo-copy-worklog.py --source 2025-03-23 --dest 2025-03-30
```

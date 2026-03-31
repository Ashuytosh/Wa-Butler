---
name: wa-scheduler
description: "Manage cron jobs. Use when user says: list schedules, remove schedule, what's scheduled, cancel reminder, stop recurring."
version: 2.0.0
---
# wa-scheduler
## LIST ALL CRON JOBS:
exec: openclaw cron list
## CREATE CRON JOB (CONFIRM FIRST):
exec: openclaw cron add --name "[name]" --cron "[schedule]" --message "[command]"
## REMOVE CRON JOB:
exec: openclaw cron rm [job-id]
## RULES
- Confirm before creating or removing any cron job

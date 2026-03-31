---
name: wa-automator
description: "Set reminders and scheduled tasks. Use when user says: remind me, schedule, every day, every week, daily, weekly, automate, set alarm, notify me."
version: 2.0.0
---
# wa-automator
## ONE-TIME REMINDER:
exec: openclaw cron add --name "[name]" --at "[duration]" --message "Reminder: [text]"
## RECURRING TASK:
exec: openclaw cron add --name "[name]" --cron "[pattern]" --message "[command or text]"
## COMMON CRON PATTERNS:
- 0 7 * * * — Every day 7 AM
- 0 19 * * * — Every day 7 PM
- 0 9 * * 1 — Every Monday 9 AM
## LIST SCHEDULED TASKS:
exec: openclaw cron list
## REMOVE A TASK:
exec: openclaw cron rm [job-id]
## RULES
- ALWAYS confirm before creating any cron job

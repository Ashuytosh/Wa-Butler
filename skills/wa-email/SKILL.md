---
name: wa-email
description: "Read, search, send emails. Use when user says: email, mail, inbox, check mail, read email, send email, compose email, any email from, what mails came."
version: 3.0.0
---

# wa-email

## READ EMAILS
### List recent inbox:
exec: gog gmail list inbox --limit 10

### Search emails:
exec: gog gmail search "[query]" --limit 10

### Read specific email:
exec: gog gmail read [EMAIL_ID]

### Unread emails:
exec: gog gmail search "is:unread" --limit 10

## SEND EMAIL
exec: gog send --to "[email]" --subject "[subject]" --body "[body]"

### Send with attachment:
exec: gog send --to "[email]" --subject "[subject]" --body "[body]" --attach "[filepath]"

## FORWARD EMAIL CONTENT TO WHATSAPP
Read the email first, then send summary via:
exec: openclaw message send -t "+[PHONE]" -m "[email summary]"

## RULES
- Always confirm before sending emails
- Show sender, subject, date, and snippet when listing
- If user asks "send this to X on WhatsApp" → use openclaw message send

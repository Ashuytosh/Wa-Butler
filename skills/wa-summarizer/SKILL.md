---
name: wa-summarizer
description: "Summarize WhatsApp messages. Use when user says: summarize, summary, what happened, catch me up, recap, brief me, digest, what did I miss, yesterday messages, last week, kya hua, batao kya chal raha."
version: 6.0.0
---

# wa-summarizer

## WHEN TO USE
User wants a summary of WhatsApp messages — single chat, group, or ALL contacts.

## STEP 1: Read contacts
exec: cat /home/YOUR_USERNAME/.openclaw/workspace/contacts.md

## STEP 2: Query messages from database
### Single contact/group:
exec: python3 /home/YOUR_USERNAME/.openclaw/workspace/scripts/msg_query.py list "[JID]" 200 "[YYYY-MM-DD]"

### Search by keyword:
exec: python3 /home/YOUR_USERNAME/.openclaw/workspace/scripts/msg_query.py search "[keyword]" "[JID]"

### All contacts summary:
Run for EACH JID in contacts.md:
exec: python3 /home/YOUR_USERNAME/.openclaw/workspace/scripts/msg_query.py list "[JID]" 50 "[TODAY]"

## STEP 3: Summarize using THIS FORMAT

### Single chat:
📋 [Name] — [Date/Range] ([X] messages)
🎯 Key Topics:
- [Topic]: [Person] — [1 line max]
📌 Decisions / Actions:
- [Person]: [action item]
📎 Attachments:
- [Person] sent [type]
⏭️ Skipped: [X] messages (greetings, ok, emojis)

### All contacts daily:
📋 Daily Summary — [Date]
👥 Active: [X] contacts, [Y] groups
📱 [Contact/Group] ([X] msgs)
- [Person]: [key point]
📌 Action Items:
- [Person]: [what needs attention]
💤 Silent: [contacts with 0 messages]

## NOTE
Message history builds over time as messages are logged. If no messages found for a contact, say "No logged messages yet for [Name]."

## RULES
- Use NAMES, never JIDs
- Skip greetings, ok, hmm, emojis
- Max 1-2 lines per person per topic
- Always mention attachments

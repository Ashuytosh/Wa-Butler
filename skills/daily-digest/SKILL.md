---
name: daily-digest
description: "Full daily summary of ALL WhatsApp and email activity. Use when user says: daily summary, what happened today, digest, catch me up on everything, brief me, what did I miss today, aaj kya hua, sab batao."
version: 4.0.0
---

# daily-digest

## WHEN TO USE
User wants a complete overview of ALL activity across WhatsApp and email.

## STEP 1: Get today's date
exec: date +%Y-%m-%d

## STEP 2: Get message stats
exec: python3 /home/YOUR_USERNAME/.openclaw/workspace/scripts/msg_query.py stats

## STEP 3: Read contacts
exec: cat /home/YOUR_USERNAME/.openclaw/workspace/contacts.md

## STEP 4: For EACH contact, query today's messages
exec: python3 /home/YOUR_USERNAME/.openclaw/workspace/scripts/msg_query.py list "[JID]" 50 "[TODAY]"

## STEP 5: Check email
exec: gog gmail search "is:unread" --limit 10

## STEP 6: Output format
📋 Daily Digest — [Date]
━━━ WHATSAPP ━━━
👥 Active: [X] contacts, [Y] groups | Total: [Z] messages
📱 [Contact/Group] ([X] msgs)
- [Person]: [key point]
━━━ EMAIL ━━━
📧 [X] emails received
- From [Sender] — [subject] — [1 line]
━━━ ACTION ITEMS ━━━
📌 [Person]: [what needs attention]
💤 Silent today: [list]

## NOTE
Message history builds over time. If database is empty, say "No messages logged yet. History will build as messages come in."

## RULES
- Use NAMES, never JIDs
- Keep summaries to 1 line per person
- Skip greetings, ok, emojis

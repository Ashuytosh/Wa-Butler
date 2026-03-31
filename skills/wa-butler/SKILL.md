---
name: wa-butler
description: "Send, read, search WhatsApp messages. Use when user wants to: send a message, read messages, list chats, search messages, check who messaged, show recent messages."
version: 7.0.0
---

# wa-butler

## WHEN TO USE
User wants to send, read, search, or list WhatsApp messages or chats.

## STEP 1: Resolve contact name to JID
exec: cat /home/YOUR_USERNAME/.openclaw/workspace/contacts.md
Find the JID for the name user mentioned. If no match, ask user.

## STEP 2: Run the right command using exec tool

### Send message (NO confirmation needed for WhatsApp):
Convert JID to phone number: remove @s.whatsapp.net, add + prefix.
Example: 917978518314@s.whatsapp.net → +917978518314

exec: openclaw message send -t "+[PHONE_NUMBER]" -m "[message text]"

### Send to a group:
exec: openclaw message send --channel whatsapp -t "[GROUP_JID]" -m "[message text]"

### List recent messages from a chat:
Message history is being migrated to SQLite. For now, inform user this feature is being rebuilt.

### Send a file:
exec: openclaw message send -t "+[PHONE_NUMBER]" --media "[file_path]" -m "[caption]"

## EXAMPLES
- "Send hi to Tanmay" → read contacts.md → find JID 917978518314@s.whatsapp.net → exec: openclaw message send -t "+917978518314" -m "hi"
- "Send hello to Sambit" → read contacts.md → find JID 918260376074@s.whatsapp.net → exec: openclaw message send -t "+918260376074" -m "hello"
- "Message game dev group" → exec: openclaw message send --channel whatsapp -t "120363424057972083@g.us" -m "[text]"

## RULES
- ALWAYS use exec tool to run commands — never print commands as text
- ALWAYS resolve name → JID from contacts.md first
- Convert JID to E.164 phone format: remove @s.whatsapp.net, add + prefix
- DO NOT use wacli — it has been removed
- DO NOT ask for confirmation for WhatsApp sends

---
name: wa-meet
description: "Create Google Meet meetings and share links. Use when user says: create meeting, schedule meet, google meet, video call, set up a call, meeting link, meet bhejo, call schedule karo."
version: 1.0.0
---

# wa-meet

## CREATE MEETING WITH GOOGLE MEET
exec: gog calendar create primary --summary "[meeting title]" --from "[YYYY-MM-DDThh:mm:ss+05:30]" --to "[YYYY-MM-DDThh:mm:ss+05:30]" --with-meet --reminder "popup:10m"

## CREATE WITH ATTENDEES
exec: gog calendar create primary --summary "[title]" --from "[start]" --to "[end]" --with-meet --attendees "[email1],[email2]" --reminder "popup:10m"

## CREATE WITH DESCRIPTION
exec: gog calendar create primary --summary "[title]" --from "[start]" --to "[end]" --with-meet --description "[agenda/details]" --reminder "popup:10m"

## SEND MEET LINK TO WHATSAPP
After creating meeting, extract the meet link from output, then:
exec: openclaw message send -t "+[PHONE]" -m "📹 Meeting: [title]\n🕐 Time: [start time] IST\n🔗 Join: [meet_link]"

## SEND TO GROUP
exec: openclaw message send --channel whatsapp -t "[GROUP_JID]" -m "📹 Meeting: [title]\n🕐 Time: [start time] IST\n🔗 Join: [meet_link]"

## LIST UPCOMING MEETINGS
exec: gog calendar list primary

## DELETE MEETING
exec: gog calendar delete primary [EVENT_ID] --force

## TIME RULES
- All times in IST (+05:30)
- Default meeting duration: 1 hour if not specified
- If user says "30 min call" → end = start + 30min

## EXAMPLES
- "Create a meeting tomorrow 3pm" → create event tomorrow 15:00-16:00 with meet
- "Schedule team call for Monday 10am, 45 mins" → create Mon 10:00-10:45 with meet
- "Send meet link to Tanmay" → create meeting → extract link → send via WhatsApp
- "Set up a call with game dev group at 8pm" → create meeting → send link to group

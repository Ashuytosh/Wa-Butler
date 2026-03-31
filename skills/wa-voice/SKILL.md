---
name: wa-voice
description: "Process voice notes from WhatsApp. Use when user says: voice, audio, voice note, listen, transcribe, what did they say in voice, process voice, sunao kya bola."
version: 6.0.0
---

# wa-voice

## WHEN TO USE
User wants to transcribe or listen to a voice note from WhatsApp.

## STEP 1: Find audio files
### List latest audio files from inbound:
exec: ls -lt /home/YOUR_USERNAME/.openclaw/media/inbound/*.ogg 2>/dev/null | head -5

### If user mentions a specific contact, check sync first:
exec: python3 /home/YOUR_USERNAME/.openclaw/workspace/scripts/sync_from_logs.py
exec: python3 /home/YOUR_USERNAME/.openclaw/workspace/scripts/msg_query.py search "audio" "[JID]"

## STEP 2: Transcribe the audio
### Transcribe latest voice note:
exec: bash /home/YOUR_USERNAME/.openclaw/workspace/scripts/process_voice.sh

### Transcribe a specific file:
exec: bash /home/YOUR_USERNAME/.openclaw/workspace/scripts/process_voice.sh "/home/YOUR_USERNAME/.openclaw/media/inbound/[filename].ogg"

### Transcribe directly with voice_to_text.sh:
exec: bash /home/YOUR_USERNAME/.openclaw/workspace/scripts/voice_to_text.sh "/home/YOUR_USERNAME/.openclaw/media/inbound/[filename].ogg"

## STEP 3: Report transcription to user
Show the transcribed text clearly.

## SEND TRANSCRIPTION TO SOMEONE
If user says "transcribe and send to X":
1. Transcribe first
2. exec: openclaw message send -t "+[PHONE]" -m "🎤 Voice note transcription: [text]"

## LANGUAGE SUPPORT
- Default: Hindi (language=hi in Groq Whisper)
- For English audio, user can specify

## EXAMPLES
- "Transcribe the last voice note" → exec: process_voice.sh
- "What did Tanmay say in voice?" → find audio from Tanmay → transcribe
- "Transcribe and send to Sambit" → transcribe → send via openclaw message send

## RULES
- ALWAYS use exec to run scripts
- Report transcription text clearly
- If no audio found, tell user "No voice notes found"
- DO NOT use wacli — audio files are at ~/.openclaw/media/inbound/

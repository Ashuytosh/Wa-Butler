---
name: wa-file-handler
description: "Download, identify, summarize files from WhatsApp. Use when user says: download file, send file, what files, check downloads, find file, media, open file, read file, summarize document."
version: 6.0.0
---

# wa-file-handler

## WHEN TO USE
User wants to find, download, identify, read, or summarize files.

## STEP 0: CHECK CACHE FIRST
exec: python3 /home/YOUR_USERNAME/.openclaw/workspace/scripts/file_handler.py get-cache "[filename]"
If NOT "CACHE_MISS" → use cached text directly.

## STEP 1: If file is already downloaded
exec: ls /home/YOUR_USERNAME/.openclaw/workspace/data/downloads/

## STEP 2: Identify file type
exec: python3 /home/YOUR_USERNAME/.openclaw/workspace/scripts/file_handler.py identify "[filepath]"

## STEP 3: Extract based on type
### PDF:
exec: python3 /home/YOUR_USERNAME/.openclaw/workspace/scripts/file_handler.py extract-pdf "[filepath]"
### DOCX:
exec: python3 /home/YOUR_USERNAME/.openclaw/workspace/scripts/file_handler.py extract-docx "[filepath]"
### TXT:
exec: python3 /home/YOUR_USERNAME/.openclaw/workspace/scripts/file_handler.py extract-txt "[filepath]"
### IMAGE: use wa-ocr skill
### AUDIO: use wa-voice skill

## STEP 4: Send file to contact
exec: openclaw message send -t "+[PHONE]" --media "[filepath]" -m "[caption]"

## RULES
- CHECK CACHE FIRST before re-downloading
- Track files in database after download
- Cleanup downloads after processing

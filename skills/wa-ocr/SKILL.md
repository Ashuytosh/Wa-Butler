---
name: wa-ocr
description: "Extract text from images using OCR. Use when user says: read image, extract text, OCR, what does this image say, screenshot text, photo text, padh isko."
version: 5.0.0
---

# wa-ocr

## WHEN TO USE
User wants to extract or read text from an image.

## IF IMAGE IS ALREADY DOWNLOADED:
exec: ls /home/YOUR_USERNAME/.openclaw/workspace/data/downloads/
exec: tesseract /home/YOUR_USERNAME/.openclaw/workspace/data/downloads/[filename] /tmp/ocr -l eng+hin && cat /tmp/ocr.txt

## SUPPORTS
- English and Hindi text
- Screenshots, photos, scanned documents

## RULES
- ALWAYS use exec to run tesseract
- Report extracted text clearly
- Cleanup after processing

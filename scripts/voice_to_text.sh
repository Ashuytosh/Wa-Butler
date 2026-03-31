#!/bin/bash
INPUT="$1"
if [ -z "$INPUT" ]; then echo "Usage: voice_to_text.sh <audio_file>"; exit 1; fi
WAV="/tmp/voice_temp.wav"
ffmpeg -y -i "$INPUT" -ar 16000 -ac 1 "$WAV" 2>/dev/null
RESULT=$(curl -s "https://api.groq.com/openai/v1/audio/transcriptions" \
  -H "Authorization: Bearer YOUR_GROQ_API_KEY" \
  -F "file=@$WAV" \
  -F "model=whisper-large-v3-turbo" \
  -F "language=hi")
echo "TRANSCRIPTION: $(echo "$RESULT" | grep -o '"text":"[^"]*"' | cut -d'"' -f4)"
rm -f "$WAV"

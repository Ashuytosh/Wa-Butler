#!/bin/bash
# Process voice notes from OpenClaw inbound media — no wacli needed
MEDIA_DIR="/home/YOUR_USERNAME/.openclaw/media/inbound"
SCRIPTS_DIR="/home/YOUR_USERNAME/.openclaw/workspace/scripts"

# If a specific file is given, use that
if [ -n "$1" ] && [ -f "$1" ]; then
    echo "Processing: $1"
    bash "$SCRIPTS_DIR/voice_to_text.sh" "$1"
    exit 0
fi

# Otherwise find the latest audio file
AUDIO_FILE=$(ls -t "$MEDIA_DIR"/*.ogg "$MEDIA_DIR"/*.opus "$MEDIA_DIR"/*.m4a "$MEDIA_DIR"/*.mp3 2>/dev/null | head -1)

if [ -z "$AUDIO_FILE" ]; then
    echo "❌ No audio files found in $MEDIA_DIR"
    exit 1
fi

echo "📎 Found: $(basename $AUDIO_FILE)"
echo "📅 Date: $(stat -c '%y' "$AUDIO_FILE" | cut -d. -f1)"
echo ""
bash "$SCRIPTS_DIR/voice_to_text.sh" "$AUDIO_FILE"

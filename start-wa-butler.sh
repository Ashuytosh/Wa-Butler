#!/bin/bash
# WA-Butler Startup Script — starts gateway + sync watcher

echo "🦞 Starting WA-Butler..."

# Step 1: Fix DNS
sudo bash -c 'echo -e "nameserver 8.8.8.8\nnameserver 8.8.4.4" > /etc/resolv.conf'
echo "✅ DNS fixed"

# Step 2: Export env vars
export GOG_ACCOUNT=YOUR_EMAIL@gmail.com
export GOG_KEYRING_PASSWORD=YOUR_GOG_PASSWORD

# Step 3: Kill any old processes
pkill -f "sync_from_logs" 2>/dev/null
pkill -f "openclaw" 2>/dev/null
sleep 2

# Step 4: Start sync watcher in background
nohup python3 ~/.openclaw/workspace/scripts/sync_from_logs.py watch > /tmp/sync_messages.log 2>&1 &
echo "✅ Sync watcher started (PID: $!)"

# Step 5: Start gateway (this stays in foreground)
echo "✅ Starting OpenClaw gateway..."
echo ""
openclaw gateway

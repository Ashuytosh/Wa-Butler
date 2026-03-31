# 🦞 WA-Butler — Personal AI WhatsApp Assistant

> Your own AI-powered WhatsApp assistant that sends messages, summarizes chats, manages email & calendar, searches the web, transcribes voice notes, extracts text from images, and more — all from your terminal.

Built on [OpenClaw](https://github.com/openclaw/openclaw) + Google Gemini 2.5 Flash + Baileys WhatsApp Web Protocol.

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-WSL2%20%7C%20Linux-blue.svg)
![Node](https://img.shields.io/badge/Node.js-22%2B-brightgreen.svg)

---

## ✨ What Can It Do?

| Feature | Description |
|---------|-------------|
| 💬 **WhatsApp Messaging** | Send/receive messages to any contact or group via CLI or TUI |
| 📋 **Chat Summarization** | Summarize any chat — per person, per group, date range, or full daily digest |
| 📧 **Email Management** | Read, search, send Gmail with attachments via `gog` CLI |
| 📅 **Google Calendar** | Create events, set reminders, view schedule |
| 📹 **Google Meet** | Generate meeting links and share via WhatsApp |
| 🔍 **Web Search** | Search the internet via DuckDuckGo (free, no API key) |
| 🎤 **Voice Transcription** | Transcribe WhatsApp voice notes (Hindi + English) via Groq Whisper |
| 📷 **OCR** | Extract text from images (Hindi + English) via Tesseract |
| 📄 **Document Processing** | Read and summarize PDFs, DOCX files with 24hr caching |
| 📁 **Google Drive** | List, search, download, upload files |
| ⏰ **Reminders & Cron** | Set one-time or recurring reminders via OpenClaw cron |
| 🗄️ **Message History** | All messages logged permanently to SQLite — searchable anytime |

---

## 🏗️ Architecture

```
WhatsApp (Baileys — single connection)
    │
    ▼
OpenClaw Gateway (port 18789)
    ├── Receives ALL messages → gateway logs (/tmp/openclaw/)
    ├── Sends messages via: openclaw message send
    ├── Agent (Gemini 2.5 Flash) processes via TUI
    │
sync_from_logs.py (background watcher, every 15s)
    │
    ▼
butler.db (SQLite — permanent storage)
    ├── messages table (inbound + outbound, deduplicated)
    ├── wa_contacts table (name, JID, phone, category)
    ├── file_cache table (extracted text, 24hr expiry)
    ├── files table (file tracking)
    │
msg_query.py (query interface)
    ├── list — chronological messages per chat
    ├── chat — conversation view
    ├── search — keyword search
    ├── stats — per-chat breakdown
    ├── digest — all chats summary
```

---

## 📋 Prerequisites

Before starting, make sure you have:

- **Windows 10/11** with WSL2 enabled (Ubuntu 24.04 recommended)
- **Node.js v22+** (required by OpenClaw)
- **Python 3.10+** (for scripts)
- **A WhatsApp account** (personal number)
- **A Google account** (for Gmail, Calendar, Drive)
- **Google Cloud Project** (free, for OAuth — setup guide below)
- **Gemini API Key** (Google AI Studio — free $300 credits available)
- **Groq API Key** (free tier — for voice transcription)

---

## 🚀 Installation (Step by Step)

### Step 1: Install WSL2 (if not already)

Open PowerShell as Administrator:
```powershell
wsl --install -d Ubuntu-24.04
```
Restart your computer, then open Ubuntu from Start menu and set up your username/password.

### Step 2: Fix DNS in WSL

Run this every time you start WSL:
```bash
sudo bash -c 'echo -e "nameserver 8.8.8.8\nnameserver 8.8.4.4" > /etc/resolv.conf'
```

### Step 3: Install Node.js v22+

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
node --version  # Should show v22.x.x
```

### Step 4: Install OpenClaw

```bash
sudo npm install -g openclaw@latest
openclaw --version
```

### Step 5: Set Up OpenClaw

```bash
openclaw onboard
```

Follow the prompts:
- Choose your LLM provider (Google Gemini recommended)
- Enter your Gemini API key
- Configure WhatsApp (scan QR code when prompted)

### Step 6: Install System Dependencies

```bash
sudo apt install -y sqlite3 ffmpeg tesseract-ocr tesseract-ocr-hin tesseract-ocr-eng python3 python3-pip
```

### Step 7: Install Homebrew + gog CLI (Google Workspace)

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.bashrc
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# Install gog (Google Workspace CLI)
brew install steipete/tap/gogcli
```

### Step 8: Install ddgr (Web Search)

```bash
sudo apt install -y ddgr
```

### Step 9: Set Up Google Cloud OAuth (for gog)

This gives WA-Butler access to your Gmail, Calendar, Drive, and Contacts.

1. **Create a Google Cloud Project:**
   - Go to: https://console.cloud.google.com/projectcreate
   - Name: `WA-Butler`
   - Click **Create**

2. **Enable APIs** — Go to each link and click **Enable** (make sure your project is selected at the top):
   - https://console.cloud.google.com/apis/library/gmail.googleapis.com
   - https://console.cloud.google.com/apis/library/calendar-json.googleapis.com
   - https://console.cloud.google.com/apis/library/drive.googleapis.com
   - https://console.cloud.google.com/apis/library/people.googleapis.com

3. **Configure OAuth Consent Screen:**
   - Go to: https://console.cloud.google.com/apis/credentials/consent
   - Select **External** → Create
   - App name: `WA-Butler`
   - User support email: your email
   - Developer email: your email
   - Click **Save and Continue** through all steps
   - On **"Audience"** page → **Add Users** → add your Gmail address

4. **Create OAuth Credentials:**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click **+ CREATE CREDENTIALS** → **OAuth client ID**
   - Application type: **Desktop app**
   - Name: `gog`
   - Click **Create** → **Download JSON**

5. **Configure gog:**
   ```bash
   mkdir -p ~/.config/gogcli/
   cp /mnt/c/Users/YOUR_WINDOWS_USERNAME/Downloads/client_secret_*.json ~/.config/gogcli/credentials.json
   
   # Use file-based keyring (simpler, no passphrase prompts)
   gog auth keyring file
   
   # Login
   gog login YOUR_EMAIL@gmail.com
   ```
   A browser window will open — authorize the app.

6. **Set environment variables:**
   ```bash
   echo 'export GOG_ACCOUNT=YOUR_EMAIL@gmail.com' >> ~/.bashrc
   echo 'export GOG_KEYRING_PASSWORD=YOUR_CHOSEN_PASSWORD' >> ~/.bashrc
   source ~/.bashrc
   ```

7. **Test:**
   ```bash
   gog calendar list primary
   gog gmail search "is:unread" --limit 5
   ```

### Step 10: Get API Keys

#### Gemini API Key (LLM Brain):
1. Go to: https://aistudio.google.com/apikey
2. Create API key
3. During `openclaw onboard`, enter this key when asked for Google provider

#### Groq API Key (Voice Transcription):
1. Go to: https://console.groq.com/keys
2. Create new API key (free tier)
3. Edit `scripts/voice_to_text.sh` and replace `YOUR_GROQ_API_KEY` with your key

---

## 📦 Project Setup

### Step 1: Clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/wa-butler.git
cd wa-butler
```

### Step 2: Copy files to OpenClaw workspace

```bash
# Copy skills
cp -r skills/* ~/.openclaw/workspace/skills/

# Copy scripts
cp scripts/* ~/.openclaw/workspace/scripts/
chmod +x ~/.openclaw/workspace/scripts/*.sh

# Copy SOUL.md
cp SOUL.md ~/.openclaw/workspace/

# Copy contacts template
cp contacts.md ~/.openclaw/workspace/

# Copy example config
cp config/openclaw.example.json ~/.openclaw/openclaw.json
```

### Step 3: Edit configuration

```bash
nano ~/.openclaw/openclaw.json
```

Update:
- Replace `YOUR_USERNAME` with your WSL username
- Replace `91XXXXXXXXXX` in `allowFrom` with your actual phone numbers (with country code)
- Replace `YOUR_GATEWAY_TOKEN_HERE` with a random token (run: `openssl rand -hex 24`)

### Step 4: Edit contacts

```bash
nano ~/.openclaw/workspace/contacts.md
```

Add your actual contacts with their WhatsApp JIDs:
- Personal: `91PHONENUMBER@s.whatsapp.net`
- Groups: `GROUPID@g.us`

### Step 5: Edit scripts paths

Replace `/home/YOUR_USERNAME` with your actual home path in:
- `SOUL.md`
- All files in `skills/*/SKILL.md`
- All files in `scripts/`

Quick command:
```bash
YOUR_USER=$(whoami)
sed -i "s|/home/YOUR_USERNAME|/home/$YOUR_USER|g" ~/.openclaw/workspace/SOUL.md
sed -i "s|/home/YOUR_USERNAME|/home/$YOUR_USER|g" ~/.openclaw/workspace/skills/*/SKILL.md
sed -i "s|/home/YOUR_USERNAME|/home/$YOUR_USER|g" ~/.openclaw/workspace/scripts/*.py ~/.openclaw/workspace/scripts/*.sh
```

### Step 6: Initialize database

```bash
python3 ~/.openclaw/workspace/scripts/db_setup.py
```

### Step 7: Link WhatsApp

```bash
openclaw channels login --channel whatsapp
```

Scan the QR code with your phone (WhatsApp → Settings → Linked Devices → Link a Device).

---

## ▶️ Starting WA-Butler

### Quick Start (one command):

```bash
bash start-wa-butler.sh
```

This handles: DNS fix → environment variables → sync watcher → gateway startup.

### Manual Start:

```bash
# Terminal 1: Fix DNS + start gateway
sudo bash -c 'echo -e "nameserver 8.8.8.8\nnameserver 8.8.4.4" > /etc/resolv.conf'
export GOG_ACCOUNT=YOUR_EMAIL@gmail.com
export GOG_KEYRING_PASSWORD=YOUR_PASSWORD
openclaw gateway

# Terminal 2: Start sync watcher + TUI
nohup python3 ~/.openclaw/workspace/scripts/sync_from_logs.py watch > /tmp/sync_messages.log 2>&1 &
openclaw tui
```

---

## 💬 Usage Examples

### In the TUI:

```
# Send a message
Send "Hey, how are you?" to Tanmay

# Summarize a chat
Summarize my chat with Sambit from last 5 days

# Daily digest
Give me a full daily digest

# Create a meeting
Create a meeting for tomorrow 3pm called "Team Standup" for 30 minutes and send the meet link to Tanmay

# Send email
Send an email to friend@gmail.com with subject "Hello" and body "Checking in!"

# Web search
Search for "latest AI news 2026"

# Voice transcription
Transcribe the last voice note

# OCR
Read text from the latest image

# Calendar
What's on my calendar today?

# Set reminder
Remind me to call Mom at 6pm today
```

### Via CLI:

```bash
# Send WhatsApp message
openclaw message send -t "+91XXXXXXXXXX" -m "Hello from WA-Butler!"

# Send to group
openclaw message send --channel whatsapp -t "120363XXXXXXX@g.us" -m "Group message"

# Send media/file
openclaw message send -t "+91XXXXXXXXXX" --media "/path/to/file.pdf" -m "Check this out"

# Check message stats
python3 ~/.openclaw/workspace/scripts/msg_query.py stats

# View conversation
python3 ~/.openclaw/workspace/scripts/msg_query.py chat "91XXXXXXXXXX@s.whatsapp.net" 50

# Search messages
python3 ~/.openclaw/workspace/scripts/msg_query.py search "keyword"

# Check Gmail
gog gmail search "is:unread" --limit 10

# Create calendar event
gog calendar create primary --summary "Meeting" --from "2026-03-29T15:00:00+05:30" --to "2026-03-29T16:00:00+05:30" --with-meet

# Web search
ddgr --num 5 --noprompt "search query"
```

---

## 📁 Project Structure

```
wa-butler/
├── README.md                          # This file
├── SOUL.md                            # AI agent identity, rules, and tools
├── contacts.md                        # Contact directory template
├── start-wa-butler.sh                 # One-command startup script
├── .gitignore                         # Git ignore rules
│
├── config/
│   └── openclaw.example.json          # Example gateway configuration
│
├── skills/                            # Custom AI skills (11 total)
│   ├── wa-butler/SKILL.md             # Core WhatsApp send/read/search
│   ├── wa-summarizer/SKILL.md         # Chat summarization
│   ├── daily-digest/SKILL.md          # Full daily digest (WhatsApp + Email)
│   ├── wa-email/SKILL.md              # Email via gog gmail
│   ├── wa-voice/SKILL.md              # Voice note transcription
│   ├── wa-ocr/SKILL.md               # Image text extraction (OCR)
│   ├── wa-file-handler/SKILL.md       # File management + document processing
│   ├── wa-automator/SKILL.md          # Reminders and scheduled tasks
│   ├── wa-scheduler/SKILL.md          # Cron job management
│   ├── web-search/SKILL.md            # Internet search via DuckDuckGo
│   └── wa-meet/SKILL.md              # Google Meet link generation
│
├── scripts/                           # Backend scripts
│   ├── sync_from_logs.py              # Gateway log → SQLite message sync
│   ├── msg_query.py                   # Message query interface
│   ├── file_handler.py                # File tracking + caching + extraction
│   ├── voice_to_text.sh               # Groq Whisper voice transcription
│   ├── process_voice.sh               # Voice note processing wrapper
│   ├── cleanup.sh                     # Download folder cleaner
│   └── db_setup.py                    # SQLite database initialization
│
└── data/                              # Runtime data (not committed)
    └── (butler.db created at runtime)
```

---

## 🔧 Skills Reference

| # | Skill | What It Does |
|---|-------|-------------|
| 1 | **wa-butler** | Core WhatsApp skill — sends messages to contacts/groups, reads history from SQLite, searches messages. Uses `openclaw message send` for sending and `msg_query.py` for reading. |
| 2 | **wa-summarizer** | Summarizes WhatsApp conversations from butler.db — single contact, group, date range, or all contacts. Formats with topics, actions, attachments, and skipped filler messages. |
| 3 | **daily-digest** | Full daily overview combining WhatsApp messages + email. Shows per-contact summary, email inbox, action items, and silent contacts. Uses `msg_query.py` + `gog gmail`. |
| 4 | **wa-email** | Email management via `gog gmail` — list inbox, search, read, send with attachments. Can forward email content to WhatsApp contacts. |
| 5 | **wa-voice** | Voice note transcription using Groq Whisper API. Finds audio from OpenClaw's inbound media, converts via ffmpeg, transcribes Hindi + English. Can forward transcription to contacts. |
| 6 | **wa-ocr** | Image text extraction using Tesseract OCR with Hindi + English support. Works on screenshots, photos, and scanned documents. |
| 7 | **wa-file-handler** | File management — identifies types (PDF/DOCX/TXT), extracts text, 24-hour SQLite cache, file tracking, sends files via WhatsApp. Routes images to wa-ocr and audio to wa-voice. |
| 8 | **wa-automator** | Creates one-time reminders and recurring scheduled tasks using OpenClaw's built-in cron system. |
| 9 | **wa-scheduler** | Manages cron jobs — list active jobs, create new, remove/cancel. Companion to wa-automator. |
| 10 | **web-search** | Internet search via ddgr (DuckDuckGo CLI). Free, no API key. Returns top 5 results. Can fetch webpage content via curl. |
| 11 | **wa-meet** | Creates Google Calendar events with Google Meet links. Shares meeting links via WhatsApp to contacts or groups. |

**Bundled skill from OpenClaw:** `gog` — full Google Workspace access (Gmail, Calendar, Drive, Contacts, Sheets, Docs).

---

## 🔧 Scripts Reference

| Script | What It Does |
|--------|-------------|
| **sync_from_logs.py** | Parses OpenClaw gateway logs + session transcripts to extract all WhatsApp messages (inbound + outbound) into butler.db. Runs as background watcher every 15 seconds. |
| **msg_query.py** | Query interface for butler.db — list messages, conversation view, keyword search, per-chat stats, digest. Used by summarization skills. |
| **file_handler.py** | File operations — identify types, extract text from PDF/DOCX/TXT, 24-hour cache in SQLite, file tracking, download cleanup. |
| **voice_to_text.sh** | Sends audio to Groq Whisper API for transcription. Converts audio to WAV via ffmpeg first. Returns Hindi/English text. |
| **process_voice.sh** | Finds latest audio file from inbound media folder and passes to voice_to_text.sh. Accepts specific file path too. |
| **cleanup.sh** | Deletes all files from the downloads folder to free space after processing. |
| **db_setup.py** | Initializes SQLite database with files, tasks, and msg_cache tables. Run once during setup. |

---

## 🗄️ Database (butler.db)

SQLite database that stores all persistent data:

| Table | What It Stores | Expires? |
|-------|---------------|----------|
| `messages` | All WhatsApp messages (inbound + outbound) | Never — grows forever |
| `wa_contacts` | Contact directory (name, JID, phone, category) | Never |
| `files` | File download tracking (name, type, sender, size) | Never |
| `file_cache` | Extracted text from documents | 24 hours |
| `tasks` | Bot task history | Never |

---

## 📱 Connected Platforms & Tools

| Platform | Tool Used | Purpose |
|----------|-----------|---------|
| WhatsApp | OpenClaw Gateway (Baileys) | Send, receive, log messages |
| Gmail | gog CLI | Read, search, send emails |
| Google Calendar | gog CLI | Events, reminders, schedule |
| Google Drive | gog CLI | File management |
| Google Meet | gog CLI | Meeting link generation |
| Google Contacts | gog CLI | Contact management |
| Web Search | ddgr (DuckDuckGo) | Free internet search |
| OCR | Tesseract | Image → text (Hindi + English) |
| Voice | Groq Whisper API | Audio → text transcription |
| LLM Brain | Google Gemini 2.5 Flash | AI processing and reasoning |

---

## ⚠️ Important Notes

### WhatsApp Limitations
- **Baileys is unofficial** — WhatsApp can ban accounts showing automation patterns. Use responsibly.
- **Single connection only** — never run two Baileys clients (like wacli) on the same number simultaneously. This corrupts encryption keys.
- **No historical messages** — message history starts from when the gateway first connects. Previous messages cannot be retrieved.
- **File sending from WhatsApp sessions** — the bot may send file paths as text instead of actual files. Use TUI for file forwarding.

### Data & Privacy
- All data stays on your machine — nothing is sent to external servers except API calls to Gemini/Groq.
- `butler.db` contains your message history — keep it secure.
- Gateway logs in `/tmp/openclaw/` are lost on WSL restart — the sync watcher captures them to butler.db before that.

### Auto-Reply
- By default, `dmPolicy` is set to `"disabled"` — the bot does NOT auto-reply to incoming WhatsApp messages.
- The bot only responds when you explicitly ask from TUI or CLI.
- Change to `"allowlist"` in `openclaw.json` if you want the bot to respond to specific contacts automatically.

---

## 🔮 Future Roadmap

- [ ] 24/7 deployment on Oracle Cloud Free Tier (Docker)
- [ ] Morning brief via cron (auto WhatsApp digest at 8 AM)
- [ ] Email watcher → WhatsApp alerts for important emails
- [ ] Better deduplication in message sync
- [ ] Gateway log persistence (backup to Google Drive)
- [ ] Group sender name resolution (WhatsApp LID mapping)
- [ ] WhatsApp-only interface (no TUI needed)

---

## 💰 Cost

| Service | Cost |
|---------|------|
| Gemini 2.5 Flash | ~₹11/day heavy use ($300 free credits ≈ 75 months) |
| Groq Whisper | Free tier |
| gog CLI | Free (uses your Google account) |
| ddgr | Free |
| OpenClaw | Free (open source) |
| Tesseract | Free (open source) |
| **Total** | **₹0/month** (while using Gemini credits) |

---

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs via Issues
- Suggest new skills or features
- Submit PRs for improvements
- Share your own skill templates

---

## 📜 License

MIT License — see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- [OpenClaw](https://github.com/openclaw/openclaw) — The AI assistant framework
- [Baileys](https://github.com/WhiskeySockets/Baileys) — WhatsApp Web API
- [gog CLI](https://github.com/steipete/gogcli) — Google Workspace CLI
- [Groq](https://groq.com) — Whisper API for voice transcription
- [Tesseract](https://github.com/tesseract-ocr/tesseract) — OCR engine
- [ddgr](https://github.com/jarun/ddgr) — DuckDuckGo search from terminal
- [Google Gemini](https://ai.google.dev/) — LLM backbone

---

**Built with 🦞 by Ashutosh Sahoo**

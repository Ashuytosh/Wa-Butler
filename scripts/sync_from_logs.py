#!/usr/bin/env python3
"""Parse OpenClaw gateway logs to extract ALL WhatsApp messages (inbound + outbound) into butler.db"""
import sqlite3
import json
import os
import glob
import re
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.expanduser("~/.openclaw/workspace/data/butler.db")
LOG_DIR = "/tmp/openclaw"
IST = timezone(timedelta(hours=5, minutes=30))

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def resolve_name(conn, phone):
    jid = phone.replace("+", "") + "@s.whatsapp.net"
    row = conn.execute("SELECT name FROM wa_contacts WHERE jid = ?", (jid,)).fetchone()
    if row:
        return row["name"], jid
    return f"Unknown ({phone[-4:]})", jid

def parse_timestamp(ts_val, fallback_time=""):
    try:
        if isinstance(ts_val, (int, float)) and ts_val > 1000000000:
            if ts_val > 10000000000:
                ts_val = ts_val / 1000
            dt = datetime.fromtimestamp(ts_val, tz=IST)
            return dt.isoformat()
    except:
        pass
    return fallback_time

def parse_log_file(filepath, conn):
    cursor = conn.cursor()
    count = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            try:
                d = json.loads(line)
                meta_name = d.get("0", "")
                msg_data = d.get("1", {})
                log_time = d.get("time", "")
                
                if not isinstance(msg_data, dict):
                    continue
                
                # === INBOUND MESSAGES (from others to you) ===
                if '"module":"web-inbound"' in meta_name:
                    if "from" in msg_data and "body" in msg_data:
                        sender_phone = msg_data["from"]
                        body = msg_data["body"]
                        timestamp = msg_data.get("timestamp", 0)
                        media_type = msg_data.get("mediaType")
                        
                        ts_str = parse_timestamp(timestamp, log_time)
                        sender_name, sender_jid = resolve_name(conn, sender_phone)
                        chat_jid = sender_jid
                        chat_name = sender_name
                        
                        # Check if it's a group message
                        if "@g.us" in str(msg_data.get("to", "")):
                            chat_jid = msg_data["to"]
                            row = conn.execute("SELECT name FROM wa_contacts WHERE jid = ?", (chat_jid,)).fetchone()
                            chat_name = row["name"] if row else f"Group ({chat_jid[:15]})"
                        
                        msg_id = f"in-{sender_phone}-{timestamp}"
                        from_me = 1 if sender_phone in ["+91XXXXXXXXXX", "91XXXXXXXXXX"] else 0
                        
                        try:
                            cursor.execute("""INSERT OR IGNORE INTO messages 
                                (chat_jid, chat_name, msg_id, sender_jid, sender_name, from_me, text, media_type, timestamp)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (chat_jid, chat_name, msg_id, sender_jid, sender_name, from_me, body, media_type, ts_str))
                            if cursor.rowcount > 0:
                                count += 1
                        except:
                            pass
                
                # === OUTBOUND MESSAGES (sent by bot/CLI via delivery-mirror) ===
                # These appear in session transcripts as delivery-mirror model
                # Also check for "Sent via gateway" log entries
                
                # Method 1: Catch outbound from auto-reply module
                if '"module":"web-auto-reply"' in meta_name:
                    if "body" in msg_data and "from" in msg_data:
                        # In auto-reply, "from" is the sender, we need to find the response
                        pass  # Responses are in session transcripts
                
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
    
    # === ALSO PARSE SESSION TRANSCRIPTS FOR OUTBOUND ===
    sessions_dir = os.path.expanduser("~/.openclaw/agents/main/sessions")
    for session_file in glob.glob(os.path.join(sessions_dir, "*.jsonl")):
        if ".reset." in session_file:
            continue
        try:
            chat_jid = None
            chat_name = None
            with open(session_file, 'r') as sf:
                for sline in sf:
                    try:
                        sd = json.loads(sline)
                        if sd.get("type") != "message":
                            continue
                        msg = sd.get("message", {})
                        ts = sd.get("timestamp", "")
                        
                        # Find session key from tool results
                        if msg.get("role") == "toolResult":
                            sk = msg.get("details", {}).get("sessionKey", "")
                            if "whatsapp:direct:" in sk:
                                phone = sk.split("direct:")[-1]
                                chat_jid = phone.replace("+", "") + "@s.whatsapp.net"
                                chat_name_row = cursor.execute("SELECT name FROM wa_contacts WHERE jid = ?", (chat_jid,)).fetchone()
                                chat_name = chat_name_row[0] if chat_name_row else f"Unknown ({phone[-4:]})"
                            elif "whatsapp:group:" in sk:
                                chat_jid = sk.split("group:")[-1]
                                chat_name_row = cursor.execute("SELECT name FROM wa_contacts WHERE jid = ?", (chat_jid,)).fetchone()
                                chat_name = chat_name_row[0] if chat_name_row else f"Group"
                        
                        # Capture delivery-mirror messages (outbound sends)
                        if msg.get("role") == "assistant" and chat_jid:
                            model = msg.get("model", "")
                            if model == "delivery-mirror":
                                content = msg.get("content", [])
                                if isinstance(content, list):
                                    for c in content:
                                        if isinstance(c, dict) and c.get("type") == "text":
                                            text = c["text"]
                                            if text and len(text) > 0:
                                                msg_id = f"out-{ts}"
                                                try:
                                                    cursor.execute("""INSERT OR IGNORE INTO messages 
                                                        (chat_jid, chat_name, msg_id, sender_jid, sender_name, from_me, text, timestamp)
                                                        VALUES (?, ?, ?, ?, ?, 1, ?, ?)""",
                                                        (chat_jid, chat_name, msg_id, "91XXXXXXXXXX@s.whatsapp.net", "Ashutosh", text, ts))
                                                    if cursor.rowcount > 0:
                                                        count += 1
                                                except:
                                                    pass
                        
                        # Capture incoming user messages with metadata
                        if msg.get("role") == "user" and chat_jid:
                            content = msg.get("content", "")
                            if isinstance(content, list):
                                for c in content:
                                    if isinstance(c, dict) and c.get("type") == "text":
                                        text = c["text"]
                                        # Extract actual message from metadata wrapper
                                        if "```" in text:
                                            parts = text.split("```")
                                            actual = parts[-1].strip()
                                            # Extract sender name
                                            sender_match = re.search(r'"sender":\s*"([^"]+)"', text)
                                            sender_id_match = re.search(r'"sender_id":\s*"([^"]+)"', text)
                                            sender_name = sender_match.group(1) if sender_match else "Unknown"
                                            sender_id = sender_id_match.group(1) if sender_id_match else ""
                                            sender_jid = sender_id.replace("+", "") + "@s.whatsapp.net" if sender_id else ""
                                            
                                            if actual and len(actual) > 0:
                                                msg_id = f"sess-{ts}"
                                                try:
                                                    cursor.execute("""INSERT OR IGNORE INTO messages 
                                                        (chat_jid, chat_name, msg_id, sender_jid, sender_name, from_me, text, timestamp)
                                                        VALUES (?, ?, ?, ?, ?, 0, ?, ?)""",
                                                        (chat_jid, chat_name, msg_id, sender_jid, sender_name, actual, ts))
                                                    if cursor.rowcount > 0:
                                                        count += 1
                                                except:
                                                    pass
                    except:
                        continue
        except:
            continue
    
    conn.commit()
    return count

def sync_all():
    conn = get_conn()
    total = 0
    
    for filepath in sorted(glob.glob(os.path.join(LOG_DIR, "openclaw-*.log"))):
        count = parse_log_file(filepath, conn)
        if count > 0:
            basename = os.path.basename(filepath)
            print(f"  📄 {basename}: {count} new messages")
        total += count
    
    conn.close()
    
    conn = get_conn()
    total_msgs = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    chats = conn.execute("SELECT COUNT(DISTINCT chat_jid) FROM messages").fetchone()[0]
    inbound = conn.execute("SELECT COUNT(*) FROM messages WHERE from_me = 0").fetchone()[0]
    outbound = conn.execute("SELECT COUNT(*) FROM messages WHERE from_me = 1").fetchone()[0]
    
    print(f"\n✅ Synced {total} new messages")
    print(f"📊 Database: {total_msgs} total ({inbound} inbound, {outbound} outbound) across {chats} chats")
    
    rows = conn.execute("""
        SELECT chat_name, COUNT(*) as cnt, 
               SUM(CASE WHEN from_me = 0 THEN 1 ELSE 0 END) as inb,
               SUM(CASE WHEN from_me = 1 THEN 1 ELSE 0 END) as outb,
               MAX(timestamp) as last_ts 
        FROM messages GROUP BY chat_jid ORDER BY last_ts DESC
    """).fetchall()
    if rows:
        print(f"\n📱 Chats:")
        for r in rows:
            print(f"  {r['chat_name']}: {r['cnt']} msgs ({r['inb']} in, {r['outb']} out) | last: {str(r['last_ts'])[:19]}")
    
    conn.close()

def watch():
    import time
    print("👁️ Watching gateway logs for new messages (inbound + outbound)...")
    while True:
        sync_all()
        time.sleep(15)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        watch()
    else:
        print("🔄 Syncing gateway logs + session transcripts → butler.db\n")
        sync_all()

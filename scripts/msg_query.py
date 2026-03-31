#!/usr/bin/env python3
"""Query WhatsApp messages from butler.db v2 — chronological, deduplicated"""
import sqlite3
import sys
import os
import json
from datetime import datetime, timedelta, timezone

DB_PATH = os.path.expanduser("~/.openclaw/workspace/data/butler.db")
IST = timezone(timedelta(hours=5, minutes=30))

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def resolve_name(jid):
    conn = get_conn()
    row = conn.execute("SELECT name FROM wa_contacts WHERE jid = ?", (jid,)).fetchone()
    conn.close()
    return row["name"] if row else f"Unknown ({jid[-14:-10]})"

def format_time(ts):
    try:
        if 'T' in str(ts):
            dt = datetime.fromisoformat(str(ts))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=IST)
            dt = dt.astimezone(IST)
        else:
            dt = datetime.fromtimestamp(float(ts), tz=IST)
        return dt.strftime("%b %d, %I:%M %p IST")
    except:
        return str(ts)[:19]

def format_time_short(ts):
    try:
        if 'T' in str(ts):
            dt = datetime.fromisoformat(str(ts))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=IST)
            dt = dt.astimezone(IST)
        else:
            dt = datetime.fromtimestamp(float(ts), tz=IST)
        return dt.strftime("%b %d, %I:%M %p")
    except:
        return str(ts)[:16]

def list_messages(chat_jid=None, limit=50, after=None, before=None):
    conn = get_conn()
    query = "SELECT * FROM messages WHERE 1=1"
    params = []
    if chat_jid:
        query += " AND chat_jid = ?"
        params.append(chat_jid)
    if after:
        query += " AND timestamp >= ?"
        params.append(after)
    if before:
        query += " AND timestamp <= ?"
        params.append(before)
    # Chronological order (oldest first for conversation view)
    query += " ORDER BY timestamp ASC LIMIT ?"
    params.append(limit)
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    results = []
    for r in rows:
        media_tag = ""
        if r["media_type"] and r["media_type"] != "None":
            mt = r["media_type"]
            if "image" in mt: media_tag = "📷 "
            elif "video" in mt: media_tag = "🎥 "
            elif "audio" in mt or "ogg" in mt: media_tag = "🎵 "
            elif "pdf" in mt or "document" in mt: media_tag = "📄 "
            elif "sticker" in mt or "webp" in mt: media_tag = "🏷️ "
            else: media_tag = "📎 "
        
        sender = r["sender_name"] or resolve_name(r["sender_jid"] or "")
        text = r["text"] or ""
        # Clean up file paths from text
        if text.startswith("/home/") and "\n" in text:
            text = text.split("\n", 1)[1].strip()
        elif text.startswith("/home/"):
            text = f"{media_tag}Sent a file"
        
        results.append({
            "time": format_time_short(r["timestamp"]),
            "sender": sender,
            "text": f"{media_tag}{text}" if media_tag and not text.startswith(media_tag) else text,
            "from_me": bool(r["from_me"]),
            "chat": r["chat_name"] or resolve_name(r["chat_jid"]),
            "media": r["media_type"] or ""
        })
    return results

def conversation_view(chat_jid, limit=50, after=None):
    """Format messages as a readable conversation"""
    msgs = list_messages(chat_jid=chat_jid, limit=limit, after=after)
    if not msgs:
        return "No messages found."
    
    chat_name = msgs[0]["chat"]
    lines = [f"📋 {chat_name} — {len(msgs)} messages\n"]
    
    for m in msgs:
        arrow = "→" if m["from_me"] else "←"
        lines.append(f"[{m['time']}] {m['sender']}: {m['text']}")
    
    return "\n".join(lines)

def search_messages(keyword, chat_jid=None, limit=50):
    conn = get_conn()
    query = "SELECT * FROM messages WHERE text LIKE ?"
    params = [f"%{keyword}%"]
    if chat_jid:
        query += " AND chat_jid = ?"
        params.append(chat_jid)
    query += " ORDER BY timestamp ASC LIMIT ?"
    params.append(limit)
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "time": format_time_short(r["timestamp"]),
            "sender": r["sender_name"] or "Unknown",
            "text": r["text"] or "",
            "chat": r["chat_name"] or r["chat_jid"],
            "from_me": bool(r["from_me"])
        })
    return results

def stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    chats = conn.execute("SELECT COUNT(DISTINCT chat_jid) FROM messages").fetchone()[0]
    inbound = conn.execute("SELECT COUNT(*) FROM messages WHERE from_me = 0").fetchone()[0]
    outbound = conn.execute("SELECT COUNT(*) FROM messages WHERE from_me = 1").fetchone()[0]
    
    today = datetime.now(IST).strftime("%Y-%m-%d")
    today_count = conn.execute("SELECT COUNT(*) FROM messages WHERE timestamp >= ?", (today,)).fetchone()[0]
    
    # Per-chat breakdown
    chat_stats = conn.execute("""
        SELECT chat_name, chat_jid, COUNT(*) as cnt,
               SUM(CASE WHEN from_me = 0 THEN 1 ELSE 0 END) as inb,
               SUM(CASE WHEN from_me = 1 THEN 1 ELSE 0 END) as outb,
               MIN(timestamp) as first_msg,
               MAX(timestamp) as last_msg
        FROM messages GROUP BY chat_jid ORDER BY MAX(timestamp) DESC
    """).fetchall()
    
    conn.close()
    
    result = {
        "total": total,
        "inbound": inbound,
        "outbound": outbound,
        "chats": chats,
        "today": today_count,
        "per_chat": []
    }
    for r in chat_stats:
        result["per_chat"].append({
            "name": r["chat_name"],
            "jid": r["chat_jid"],
            "total": r["cnt"],
            "inbound": r["inb"],
            "outbound": r["outb"],
            "first": str(r["first_msg"])[:10],
            "last": str(r["last_msg"])[:10]
        })
    return result

def all_chats_summary(after=None):
    """Get summary of all chats for digest"""
    conn = get_conn()
    query = """
        SELECT chat_name, chat_jid, COUNT(*) as cnt,
               SUM(CASE WHEN from_me = 0 THEN 1 ELSE 0 END) as inb,
               SUM(CASE WHEN from_me = 1 THEN 1 ELSE 0 END) as outb
        FROM messages WHERE 1=1
    """
    params = []
    if after:
        query += " AND timestamp >= ?"
        params.append(after)
    query += " GROUP BY chat_jid HAVING cnt > 0 ORDER BY MAX(timestamp) DESC"
    
    chats = conn.execute(query, params).fetchall()
    
    result = []
    for chat in chats:
        # Get messages for this chat
        msg_query = "SELECT * FROM messages WHERE chat_jid = ?"
        msg_params = [chat["chat_jid"]]
        if after:
            msg_query += " AND timestamp >= ?"
            msg_params.append(after)
        msg_query += " ORDER BY timestamp ASC LIMIT 100"
        
        msgs = conn.execute(msg_query, msg_params).fetchall()
        
        messages = []
        for m in msgs:
            text = m["text"] or ""
            media_tag = ""
            if m["media_type"] and m["media_type"] != "None":
                mt = m["media_type"]
                if "image" in mt: media_tag = "📷 "
                elif "pdf" in mt or "document" in mt: media_tag = "📄 "
                elif "audio" in mt: media_tag = "🎵 "
                elif "video" in mt: media_tag = "🎥 "
                elif "sticker" in mt or "webp" in mt: media_tag = "🏷️ "
                else: media_tag = "📎 "
            
            if text.startswith("/home/"):
                text = "Sent a file"
            
            messages.append({
                "time": format_time_short(m["timestamp"]),
                "sender": m["sender_name"] or "Unknown",
                "text": f"{media_tag}{text}" if media_tag else text,
                "from_me": bool(m["from_me"])
            })
        
        result.append({
            "name": chat["chat_name"],
            "jid": chat["chat_jid"],
            "total": chat["cnt"],
            "inbound": chat["inb"],
            "outbound": chat["outb"],
            "messages": messages
        })
    
    conn.close()
    return result

def log_message(chat_jid, chat_name, sender_jid, sender_name, from_me, text, media_type=None, msg_id=None):
    conn = get_conn()
    # Normalize JID
    if chat_jid.startswith("+"):
        chat_jid = chat_jid[1:]
    if "@" not in chat_jid and "@g.us" not in chat_jid:
        chat_jid = chat_jid + "@s.whatsapp.net"
    
    ts = datetime.now(IST).isoformat()
    try:
        conn.execute("""INSERT OR IGNORE INTO messages 
            (chat_jid, chat_name, msg_id, sender_jid, sender_name, from_me, text, media_type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (chat_jid, chat_name, msg_id or f"manual-{ts}", sender_jid, sender_name, 1 if from_me else 0, text, media_type, ts))
        conn.commit()
        print(f"✅ Logged message from {sender_name} in {chat_name}")
    except Exception as e:
        print(f"❌ Error logging: {e}")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: msg_query.py <command> [args]")
        print("Commands: list, chat, search, stats, digest, contacts, log")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        chat = sys.argv[2] if len(sys.argv) > 2 else None
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        after = sys.argv[4] if len(sys.argv) > 4 else None
        results = list_messages(chat_jid=chat, limit=limit, after=after)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif cmd == "chat":
        # Conversation view — nice formatted output
        chat = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        after = sys.argv[4] if len(sys.argv) > 4 else None
        print(conversation_view(chat, limit, after))
    
    elif cmd == "search":
        keyword = sys.argv[2]
        chat = sys.argv[3] if len(sys.argv) > 3 else None
        results = search_messages(keyword, chat_jid=chat)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif cmd == "stats":
        s = stats()
        print(json.dumps(s, indent=2, ensure_ascii=False))
    
    elif cmd == "digest":
        after = sys.argv[2] if len(sys.argv) > 2 else None
        result = all_chats_summary(after)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "contacts":
        conn = get_conn()
        rows = conn.execute("SELECT name, jid, category FROM wa_contacts ORDER BY category, name").fetchall()
        conn.close()
        for r in rows:
            print(f"{r['category']:6s} | {r['name']:15s} | {r['jid']}")
    
    elif cmd == "log":
        log_message(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5],
                   sys.argv[6] == "1", sys.argv[7],
                   sys.argv[8] if len(sys.argv) > 8 else None)
    
    else:
        print(f"Unknown command: {cmd}")

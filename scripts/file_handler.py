#!/usr/bin/env python3
"""File handler: download, identify, summarize, track, cleanup with 24hr cache"""
import sqlite3
import subprocess
import sys
import os
import json
from datetime import datetime, timedelta

DB_PATH = "/home/YOUR_USERNAME/.openclaw/workspace/data/butler.db"
DL_DIR = "/home/YOUR_USERNAME/.openclaw/workspace/data/downloads"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    # Create cache table if not exists
    conn.execute('''CREATE TABLE IF NOT EXISTS file_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        filetype TEXT,
        sender TEXT,
        chat_jid TEXT,
        chat_name TEXT,
        extracted_text TEXT,
        summary TEXT,
        cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        expires_at DATETIME
    )''')
    conn.commit()
    return conn

def cache_file(filename, filetype, sender, chat_jid, chat_name, extracted_text):
    conn = get_db()
    expires = datetime.utcnow() + timedelta(hours=24)
    conn.execute(
        "INSERT INTO file_cache (filename, filetype, sender, chat_jid, chat_name, extracted_text, expires_at) VALUES (?,?,?,?,?,?,?)",
        (filename, filetype, sender, chat_jid, chat_name, extracted_text, expires)
    )
    conn.commit()
    conn.close()
    return f"✅ Cached: {filename} (expires in 24hrs)"

def get_cached(filename):
    conn = get_db()
    row = conn.execute(
        "SELECT extracted_text, summary, cached_at FROM file_cache WHERE filename=? AND expires_at > ? ORDER BY cached_at DESC LIMIT 1",
        (filename, datetime.utcnow())
    ).fetchone()
    conn.close()
    if row:
        return {"text": row[0], "summary": row[1], "cached_at": row[2]}
    return None

def update_summary(filename, summary):
    conn = get_db()
    conn.execute(
        "UPDATE file_cache SET summary=? WHERE filename=? AND expires_at > ? ORDER BY cached_at DESC LIMIT 1",
        (summary, filename, datetime.utcnow())
    )
    conn.commit()
    conn.close()
    return f"✅ Summary saved for {filename}"

def search_cache(keyword):
    conn = get_db()
    rows = conn.execute(
        "SELECT filename, filetype, sender, chat_name, cached_at FROM file_cache WHERE (extracted_text LIKE ? OR summary LIKE ? OR filename LIKE ?) AND expires_at > ?",
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", datetime.utcnow())
    ).fetchall()
    conn.close()
    if not rows:
        return "No cached files match that keyword."
    lines = []
    for r in rows:
        lines.append(f"• {r[0]} ({r[1]}) from {r[2]} in {r[3]} — cached {r[4][:16]}")
    return "\n".join(lines)

def clean_expired():
    conn = get_db()
    deleted = conn.execute(
        "DELETE FROM file_cache WHERE expires_at < ?", (datetime.utcnow(),)
    ).rowcount
    conn.commit()
    conn.close()
    return f"🗑️ Cleaned {deleted} expired cache entries"

def track_file(filename, filetype, sender, chat_jid, chat_name, file_path):
    conn = get_db()
    size = 0
    if os.path.exists(file_path):
        size = os.path.getsize(file_path) // 1024
    conn.execute(
        "INSERT INTO files (filename, filetype, sender, chat_jid, chat_name, file_path, file_size_kb) VALUES (?,?,?,?,?,?,?)",
        (filename, filetype, sender, chat_jid, chat_name, file_path, size)
    )
    conn.commit()
    conn.close()
    return f"✅ Tracked: {filename} ({filetype}, {size}KB)"

def identify_type(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    type_map = {
        '.pdf': 'pdf', '.docx': 'docx', '.doc': 'doc', '.txt': 'text',
        '.xlsx': 'excel', '.xls': 'excel', '.csv': 'csv',
        '.png': 'image', '.jpg': 'image', '.jpeg': 'image', '.webp': 'image',
        '.mp4': 'video', '.oga': 'audio', '.ogg': 'audio', '.mp3': 'audio',
        '.zip': 'archive', '.rar': 'archive'
    }
    return type_map.get(ext, 'unknown')

def extract_text_pdf(filepath):
    result = subprocess.run(['pdftotext', filepath, '-'], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else "❌ Failed to extract PDF text"

def extract_text_docx(filepath):
    result = subprocess.run(['pandoc', filepath, '-t', 'plain'], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else "❌ Failed to extract DOCX text"

def extract_text_txt(filepath):
    with open(filepath, 'r', errors='ignore') as f:
        return f.read().strip()

def get_storage_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*), COALESCE(SUM(file_size_kb),0) FROM files WHERE status='downloaded'").fetchone()
    cleaned = conn.execute("SELECT COUNT(*) FROM files WHERE status='cleaned'").fetchone()
    cached = conn.execute("SELECT COUNT(*) FROM file_cache WHERE expires_at > ?", (datetime.utcnow(),)).fetchone()
    conn.close()
    return f"📁 Active files: {total[0]} ({total[1]}KB) | Cleaned: {cleaned[0]} | Cached: {cached[0]}"

def cleanup_downloads():
    count = 0
    for f in os.listdir(DL_DIR):
        fpath = os.path.join(DL_DIR, f)
        if os.path.isfile(fpath):
            os.remove(fpath)
            count += 1
    conn = get_db()
    conn.execute("UPDATE files SET status='cleaned', cleaned_at=? WHERE status='downloaded'", (datetime.now(),))
    conn.commit()
    conn.close()
    return f"🗑️ Cleaned {count} files from downloads"

def list_tracked(limit=10):
    conn = get_db()
    rows = conn.execute(
        "SELECT filename, filetype, sender, chat_name, downloaded_at, status FROM files ORDER BY downloaded_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    if not rows:
        return "No files tracked yet."
    lines = []
    for r in rows:
        lines.append(f"• {r[0]} ({r[1]}) from {r[2]} in {r[3]} — {r[4][:10]} [{r[5]}]")
    return "\n".join(lines)

def list_cache():
    conn = get_db()
    rows = conn.execute(
        "SELECT filename, filetype, sender, chat_name, cached_at, expires_at FROM file_cache WHERE expires_at > ? ORDER BY cached_at DESC",
        (datetime.utcnow(),)
    ).fetchall()
    conn.close()
    if not rows:
        return "No cached files."
    lines = []
    for r in rows:
        lines.append(f"• {r[0]} ({r[1]}) from {r[2]} in {r[3]} — cached {r[4][:16]} — expires {r[5][:16]}")
    return "\n".join(lines)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "track":
        print(track_file(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7]))
    elif cmd == "identify":
        print(identify_type(sys.argv[2]))
    elif cmd == "extract-pdf":
        print(extract_text_pdf(sys.argv[2]))
    elif cmd == "extract-docx":
        print(extract_text_docx(sys.argv[2]))
    elif cmd == "extract-txt":
        print(extract_text_txt(sys.argv[2]))
    elif cmd == "cache":
        print(cache_file(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7]))
    elif cmd == "get-cache":
        result = get_cached(sys.argv[2])
        if result:
            print(json.dumps(result))
        else:
            print("CACHE_MISS")
    elif cmd == "save-summary":
        print(update_summary(sys.argv[2], sys.argv[3]))
    elif cmd == "search-cache":
        print(search_cache(sys.argv[2]))
    elif cmd == "clean-expired":
        print(clean_expired())
    elif cmd == "list-cache":
        print(list_cache())
    elif cmd == "stats":
        print(get_storage_stats())
    elif cmd == "cleanup":
        print(cleanup_downloads())
    elif cmd == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print(list_tracked(limit))
    else:
        print("Commands: track, identify, extract-pdf, extract-docx, extract-txt, cache, get-cache, save-summary, search-cache, clean-expired, list-cache, stats, cleanup, list")

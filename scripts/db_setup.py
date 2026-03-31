#!/usr/bin/env python3
import sqlite3
import os

DB_PATH = "/home/YOUR_USERNAME/.openclaw/workspace/data/butler.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# File tracking table
c.execute('''CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filetype TEXT,
    sender TEXT,
    chat_jid TEXT,
    chat_name TEXT,
    downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_path TEXT,
    file_size_kb INTEGER,
    status TEXT DEFAULT 'downloaded',
    summary TEXT,
    cleaned_at DATETIME
)''')

# Task history table
c.execute('''CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,
    query TEXT,
    result TEXT,
    status TEXT DEFAULT 'completed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)''')

# Message cache (avoid re-processing)
c.execute('''CREATE TABLE IF NOT EXISTS msg_cache (
    msg_id TEXT PRIMARY KEY,
    chat_jid TEXT,
    sender TEXT,
    content TEXT,
    msg_type TEXT,
    timestamp DATETIME,
    processed INTEGER DEFAULT 0
)''')

conn.commit()
conn.close()
print("✅ Database created at", DB_PATH)

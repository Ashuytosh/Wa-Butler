---
name: web-search
description: "Search the web for information. Use when user says: search, google, look up, find out, what is, who is, latest news, search for, kya hai, batao about, tell me about."
version: 1.0.0
---

# web-search

## WHEN TO USE
User wants to search the internet for any information, news, facts, or answers.

## SEARCH (use ddgr — DuckDuckGo search)
exec: ddgr --num 5 --noprompt "[SEARCH_QUERY]"

## FETCH A WEBPAGE (if user gives a URL)
exec: curl -sL "[URL]" | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub('<[^>]+>', ' ', html)
text = re.sub('\s+', ' ', text).strip()
print(text[:3000])
"

## SEND RESULTS TO WHATSAPP
If user says "search X and send to Y":
1. Search first
2. Format results cleanly
3. exec: openclaw message send -t "+[PHONE]" -m "[search results]"

## EXAMPLES
- "Search for latest AI news" → exec: ddgr --num 5 --noprompt "latest AI news"
- "What is OpenClaw?" → exec: ddgr --num 5 --noprompt "OpenClaw AI assistant"
- "Look up Python async await tutorial" → exec: ddgr --num 5 --noprompt "Python async await tutorial"
- "Search and send results to Tanmay" → search + exec: openclaw message send

## RULES
- Always use ddgr for web searches
- Show max 5 results with title, URL, and snippet
- If user asks to send results, use openclaw message send
- Keep results concise

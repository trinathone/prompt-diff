# prompt-diff

Ever spent an hour tweaking a system prompt, then wondered: "Wait — what did I actually change? Did I just add 300 tokens without noticing?"

prompt-diff is a local web tool that shows you exactly what changed between two versions of a prompt — character by character, line by line, token by token.

## Real situations where this saves you

1. You're iterating on a RAG system prompt. After 6 versions you can't remember what changed between v3 and v5 that broke the eval scores.

2. You paste two conversation JSON blobs and instantly see which turns were added, removed, or changed — without squinting at raw JSON.

3. Your token budget is tight. You paste old vs new and see `+56 tokens` in red before it hits prod.

4. You handed off a prompt to a teammate and they "fixed it" — now you need to see what they actually changed.

## What it shows you

- Side-by-side colored diff (green = added, red = removed)
- Exact token count for each version, and the delta
- Character-level highlights within changed lines
- If it's a conversation JSON: how many turns were added/removed, which roles changed
- Plain English summary: "3 lines added, 1 removed. Token count went from 142 → 198 (+56)."

## How it works

1. Open http://localhost:8009
2. Paste Prompt A on the left, Prompt B on the right
3. Click "Diff →" (or Ctrl+Enter)
4. See the diff, token counts, and summary instantly
5. Toggle "Turn View" if your prompt is a JSON conversation array

Runs 100% locally — no data leaves your machine.

## Quick start

```bash
pip install -r requirements.txt
uvicorn main:app --port 8009
# open http://localhost:8009
```

## API

```
POST /diff          — compute diff between two prompts
POST /tokenize      — count tokens in a string
POST /enhance       — NIM-powered insight on what the change means
GET  /health        — health check
```

## Stack

Python 3.11 · FastAPI · difflib (stdlib) · zero npm

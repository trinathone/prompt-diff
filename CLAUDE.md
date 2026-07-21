# prompt-diff — CLAUDE.md Build Spec

## What it is
A local web tool that shows a live side-by-side diff between two versions of an LLM prompt or conversation, with token count and structural change summary.

## Why it exists
ML engineers iterate on system prompts dozens of times per day. Right now they paste prompts into generic text diff tools that don't understand prompt structure — they don't highlight added/removed turns, count token deltas, or flag when a role changed from `user` to `assistant`. This causes silent regressions where a tweaked system prompt cuts 300 tokens and the engineer doesn't notice until eval scores drop.

**Evidence:**
- MLflow GitHub FR "Comparing different artifacts in comparison view" — 36 👍 (https://github.com/mlflow/mlflow/issues)
- LiteLLM bug: "reasoning_content stripped from assistant messages in multi-turn" — 25 👍
- HN thread: "Ask HN: I hate coding agents. Is this skill issue?" — devs complaining about prompt iteration loops with no visibility

## Stack
- FastAPI + Python 3.11
- Single-page HTML UI — inline JS/CSS, no build step
- Dark theme: #0d1117 background, #161b22 panels, #00ff88 accent
- Port: **8009**

## File structure
```
prompt-diff/
├── main.py              # FastAPI app
├── diff_engine.py       # Tokenizer + diff logic
├── requirements.txt
├── static/
│   └── index.html       # Full single-page UI
└── README.md
```

## API Endpoints

### POST /diff
Request:
```json
{
  "left": "string — prompt A (plain text or JSON conversation array)",
  "right": "string — prompt B"
}
```
Response:
```json
{
  "hunks": [
    {
      "type": "equal|insert|delete|replace",
      "left_lines": ["line1", ...],
      "right_lines": ["line1", ...],
      "left_start": 0,
      "right_start": 0
    }
  ],
  "stats": {
    "left_tokens": 142,
    "right_tokens": 198,
    "token_delta": 56,
    "lines_added": 3,
    "lines_removed": 1,
    "is_json_conversation": true,
    "turns_added": 1,
    "turns_removed": 0,
    "roles_changed": []
  }
}
```

### POST /tokenize
Request:
```json
{"text": "string"}
```
Response:
```json
{"token_count": 42, "char_count": 180}
```

### GET /health
Response: `{"status": "ok", "port": 8009}`

## UI Design

**Layout:** Two columns left/right with diff display below.

**Header bar:** `prompt-diff` in monospace, token counts for each side showing delta in green (added) or red (removed).

**Input area:**
- Two side-by-side textareas, dark bg (#0d1117), monospace font, min-height 200px
- Left textarea label: "Prompt A" / Right: "Prompt B"
- Both have placeholder: "Paste your system prompt or conversation JSON here..."
- "Diff →" button centered, green accent (#00ff88), runs on click AND on Ctrl+Enter

**Stats bar** (between input and diff):
- Shows: left tokens | right tokens | Δ tokens | lines added/removed
- If JSON conversation detected: shows turns added/removed
- Token delta shown as `+56 tokens` in green or `-30 tokens` in red

**Diff view:**
- Unified diff style with line numbers
- Inserted lines: #1a3a1a background, left border 3px #00ff88
- Deleted lines: #3a1a1a background, left border 3px #ff4444
- Equal lines: #161b22 background
- Character-level highlights: bright green for added chars, bright red for deleted chars within changed lines
- If JSON conversation: also show a "Turn view" toggle that renders each message role as a colored badge (system=purple, user=blue, assistant=green)

**Side panel (right):** Shows structural summary in plain English:
- "3 lines added, 1 removed"
- "Token count went from 142 → 198 (+56)"
- "1 new turn added (user)"
- "No roles changed"

**Footer:** `port 8009 · local only · no data leaves your machine`

## Diff Engine (diff_engine.py)

Use Python's built-in `difflib.SequenceMatcher` for line diffs and `difflib.ndiff` for character-level highlights within changed lines.

Token counting: Use a simple whitespace+punctuation tokenizer (no tiktoken dependency) — count by splitting on whitespace and punctuation. Approximate is fine.

JSON conversation detection: Try to parse input as JSON. If it's a list of dicts with `role` and `content` keys → it's a conversation. Compare turn by turn.

## NVIDIA NIM Usage

Import inside functions only, never at module level:

```python
# Example usage inside a function:
def some_nim_function(text: str):
    import sys
    sys.path.insert(0, os.path.expanduser("~/keys"))
    from api_keys import NVIDIA_NIM_KEY
    # ... use key
```

This project does NOT need NIM for core functionality (diff is local). NIM is optional — add a `/enhance` endpoint that uses `meta/llama-4-scout-17b-16e-instruct` to suggest why the prompt changed and what the impact might be.

### POST /enhance (optional, NIM-powered)
Request:
```json
{
  "left": "string",
  "right": "string",
  "diff_stats": {}
}
```
Response:
```json
{
  "insight": "The system prompt now explicitly restricts the model to only answer in English, which may reduce response diversity for multilingual users but improves consistency.",
  "risk": "low|medium|high",
  "model_used": "meta/llama-4-scout-17b-16e-instruct"
}
```

## Rules
- DO NOT start the server
- DO NOT make any API calls during build
- Syntax check must pass: `python3 -m py_compile main.py diff_engine.py`
- All code in one pass — no stubs, complete implementation
- UI must be fully functional: paste two prompts → click Diff → see results
- requirements.txt must list all deps
- No external CSS frameworks, no npm, no node

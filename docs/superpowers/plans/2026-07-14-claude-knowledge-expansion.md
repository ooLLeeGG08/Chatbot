# Claude Knowledge Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the DuckDuckGo Instant Answer fallback in the chatbot with a Claude API (Haiku 4.5) call, so the bot can answer a much broader range of questions, while keeping small talk/arithmetic instant and the bot stateless.

**Architecture:** `google_search.py` is renamed to `answer_engine.py`. Small talk and calculator logic are unchanged. The DuckDuckGo-specific helpers and the `_query_duckduckgo` call are removed and replaced with `_query_claude`, which calls `client.messages.create(...)` on the official `anthropic` SDK. `server.py`'s import is updated to match.

**Tech Stack:** Python, Flask, `anthropic` SDK, `python-dotenv`.

## Global Constraints

- No conversation history is sent to Claude — each call is independent (stateless).
- Model is `claude-haiku-4-5`, `max_tokens=300`.
- Small talk and arithmetic must continue to resolve without any API call.
- No automated test suite exists in this repo — verification is manual (per the approved spec's Testing section).
- Do not commit changes — the user will review and commit in PyCharm themselves.

---

### Task 1: Dependencies and secret config for the Claude API

**Files:**
- Modify: `requirements.txt`
- Modify: `.gitignore`
- Create: `.env.example`

**Interfaces:**
- Produces: `ANTHROPIC_API_KEY` environment variable, read by Task 2's `answer_engine.py` via `load_dotenv()`.

- [ ] **Step 1: Update `requirements.txt`**

Current content:
```
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
gunicorn==21.2.0
```

New content (`requests` is dropped — nothing in the codebase uses it once `_query_duckduckgo` is removed in Task 2; `anthropic` and `python-dotenv` are added):
```
Flask==2.3.3
Flask-CORS==4.0.0
gunicorn==21.2.0
anthropic>=0.40.0
python-dotenv>=1.0
```

- [ ] **Step 2: Add `.env` to `.gitignore`**

Current `.gitignore`:
```
.idea/
venv/
.venv/
__pycache__/
*.pyc
.DS_Store
```

Add a line so it reads:
```
.idea/
venv/
.venv/
__pycache__/
*.pyc
.DS_Store
.env
```

- [ ] **Step 3: Create `.env.example`**

```
ANTHROPIC_API_KEY=
```

- [ ] **Step 4: Verify**

Run: `grep -n "anthropic\|python-dotenv" requirements.txt && grep -n "^\.env$" .gitignore && cat .env.example`
Expected: both packages listed in `requirements.txt`, `.env` present in `.gitignore`, `.env.example` contains the one line above.

---

### Task 2: Implement `answer_engine.py` (rename + Claude integration)

**Files:**
- Create: `answer_engine.py` (replaces `google_search.py`)
- Delete: `google_search.py`

**Interfaces:**
- Consumes: `ANTHROPIC_API_KEY` from environment (Task 1).
- Produces: `chatbot_query(query: str) -> str` — same signature as before, consumed by `server.py` (Task 3).

- [ ] **Step 1: Write `answer_engine.py`**

```python
import ast
import operator
import re
import os

import anthropic
from dotenv import load_dotenv

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_SMALL_TALK = (
    (("hello", "hi", "hey", "hiya", "yo"), "Hello! How can I help you today?"),
    (("how are you", "how're you", "how you doing", "how are u"), "I'm doing well, thanks for asking! What can I help you with?"),
    (("thanks", "thank you", "thx"), "You're welcome!"),
    (("bye", "goodbye", "see you", "see ya"), "Goodbye! Come back anytime."),
    (("good morning",), "Good morning! What can I help you with?"),
    (("good afternoon",), "Good afternoon! What can I help you with?"),
    (("good evening",), "Good evening! What can I help you with?"),
    (("who are you", "what are you"), "I'm a chatbot that can answer questions and do simple math!"),
)

SYSTEM_PROMPT = (
    "You are a concise, friendly chatbot embedded in a small web widget. "
    "Give direct, factual answers in 1-3 sentences unless asked for more "
    "detail. If you don't know, say so plainly instead of guessing."
)

load_dotenv()
client = anthropic.Anthropic()


def _try_small_talk(query):
    normalized = re.sub(r'[^a-z\s]', '', query.strip().lower()).strip()
    for phrases, reply in _SMALL_TALK:
        if normalized in phrases:
            return reply
    return None


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_eval_node(node.operand))
    raise ValueError("unsupported expression")


def _try_calculate(query):
    expression = query.strip().rstrip('?')
    if not re.fullmatch(r'[0-9\.\s+\-*/()]+', expression):
        return None
    try:
        tree = ast.parse(expression, mode='eval')
        return _eval_node(tree.body)
    except Exception:
        return None


def _query_claude(query):
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": query}],
    )
    return next(block.text for block in response.content if block.type == "text")


def chatbot_query(query):
    fallback = 'Sorry, I cannot think of a reply for that.'

    small_talk_reply = _try_small_talk(query)
    if small_talk_reply is not None:
        return small_talk_reply

    calculation = _try_calculate(query)
    if calculation is not None:
        if isinstance(calculation, float) and calculation.is_integer():
            calculation = int(calculation)
        return str(calculation)

    try:
        return _query_claude(query)
    except anthropic.AuthenticationError as e:
        print(f"answer_engine error (auth): {e}")
        return fallback
    except anthropic.RateLimitError as e:
        print(f"answer_engine error (rate limit): {e}")
        return fallback
    except anthropic.APIStatusError as e:
        print(f"answer_engine error (status {e.status_code}): {e}")
        return fallback
    except anthropic.APIConnectionError as e:
        print(f"answer_engine error (connection): {e}")
        return fallback
```

- [ ] **Step 2: Delete the old file**

Run: `rm google_search.py`

- [ ] **Step 3: Verify small talk and arithmetic still resolve without any API call**

Run:
```bash
python3 -c "
import os
os.environ.setdefault('ANTHROPIC_API_KEY', 'unset-for-local-check')
from answer_engine import chatbot_query
print(chatbot_query('hello'))
print(chatbot_query('2 + 2'))
"
```
Expected output:
```
Hello! How can I help you today?
4
```
(No network call is made for either line — both resolve before `_query_claude` is reached.)

- [ ] **Step 4: Verify the Claude path (requires a real `ANTHROPIC_API_KEY` in `.env`)**

Run:
```bash
python3 -c "
from answer_engine import chatbot_query
print(chatbot_query('What is the capital of France?'))
"
```
Expected: a short factual answer mentioning Paris. If `ANTHROPIC_API_KEY` is missing or invalid, expect the fallback string `Sorry, I cannot think of a reply for that.` printed to stdout via the `answer_engine error (auth): ...` log line on stderr — not a crash.

---

### Task 3: Wire `server.py` to the renamed module

**Files:**
- Modify: `server.py:4`

**Interfaces:**
- Consumes: `chatbot_query` from `answer_engine` (Task 2).

- [ ] **Step 1: Update the import**

Change:
```python
from google_search import chatbot_query
```
to:
```python
from answer_engine import chatbot_query
```

- [ ] **Step 2: Verify the server starts and the endpoint responds**

Run (with `ANTHROPIC_API_KEY` set in `.env`):
```bash
python3 server.py &
sleep 2
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"message":"What is the capital of France?"}' \
  http://localhost:8080/api/chat
kill %1
```
Expected: JSON response `{"response": "...", "status": "success"}` with a Paris-related answer.

---

### Task 4: Update `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the setup and feature description**

In the "Quick Start" / "Manual installation" section, add a step for the API key before `python3 server.py`:
```
export ANTHROPIC_API_KEY=your_api_key_here
```
(or set it in a local `.env` file, matching `.env.example`).

In the "How It Works" section, update step 3 to read:
```
3. **Answer Resolution** (`answer_engine.py`), in order:
   - Small talk (greetings, thanks, etc.) matched against a fixed phrase list
   - Simple arithmetic, evaluated safely via a restricted AST parser
   - Otherwise, a question answered by the Claude API (Haiku 4.5)
```

Update the "Modifying Answer Behavior" customization note to reference `answer_engine.py` instead of `google_search.py` (already done in the prior cleanup pass — confirm it still reads correctly).

Add a line noting the required `ANTHROPIC_API_KEY` environment variable to each deployment option already documented (Heroku, Railway, Render, Docker) alongside their existing setup steps.

- [ ] **Step 2: Verify**

Run: `grep -n "ANTHROPIC_API_KEY\|answer_engine" README.md`
Expected: several matches confirming the key and module name are documented.

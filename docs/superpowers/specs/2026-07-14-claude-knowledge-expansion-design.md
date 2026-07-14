# Expand chatbot knowledge via the Claude API

## Problem

The chatbot currently answers general questions via the DuckDuckGo Instant
Answer API, which only returns results for topics DuckDuckGo has a curated
infobox/definition for — most ordinary questions fall through to "Sorry, I
cannot think of a reply for that." Small talk and arithmetic are handled
locally and work fine; only the general-knowledge fallback is limited.

## Goals

- Replace the DuckDuckGo fallback with a call to the Claude API so the bot
  can answer a much broader range of questions.
- Keep small talk and arithmetic answered locally (free, instant) — only
  genuine questions should cost an API call.
- Keep the chatbot stateless (no multi-turn memory), matching current
  behavior.

## Non-goals

- Multi-turn conversation memory / session state.
- Removing or changing the small-talk or calculator logic.
- Any frontend (`app.js`, `index.html`, `style.css`) changes — the
  `/api/chat` request/response shape is unchanged.

## Architecture

`google_search.py` is renamed to `answer_engine.py` (its current name is
already misleading — no Google API is used). The resolution order inside
`chatbot_query` stays the same shape, with the last step replaced:

```
user message -> small talk? -> calculator? -> Claude (Haiku 4.5) -> fallback string
```

`server.py`'s import updates from `from google_search import chatbot_query`
to `from answer_engine import chatbot_query`. No other server changes.

The DuckDuckGo-specific query-shaping helpers (`_simplify_question`,
`_QUESTION_PREFIXES`, `_query_duckduckgo`) are deleted — they existed only to
fit DuckDuckGo's narrow Instant-Answer API and aren't needed for a
general-purpose LLM call.

## Components & data flow

- `client = anthropic.Anthropic()` at module load in `answer_engine.py`,
  reading `ANTHROPIC_API_KEY` from the environment via `load_dotenv()`
  (same pattern as the WeatherApp project).
- `_query_claude(query: str) -> str`: calls
  `client.messages.create(model="claude-haiku-4-5", max_tokens=300, system=SYSTEM_PROMPT, messages=[{"role": "user", "content": query}])`
  and returns the response's text content.
- `SYSTEM_PROMPT`: "You are a concise, friendly chatbot embedded in a small
  web widget. Give direct, factual answers in 1-3 sentences unless asked for
  more detail. If you don't know, say so plainly instead of guessing."
- `chatbot_query(query)`: small talk -> calculator -> `_query_claude(query)`
  -> fallback string on any failure. The raw user query is passed to Claude
  as-is (no simplification needed).
- No conversation history is sent — each call is independent (stateless, per
  Goals).

## Error handling

`_query_claude` wraps the API call and catches, most-specific first:
`anthropic.AuthenticationError` (missing/invalid key),
`anthropic.RateLimitError`, `anthropic.APIStatusError`, and
`anthropic.APIConnectionError`. On any of these, log the error server-side
(`print(...)`, matching the existing DuckDuckGo error-handling style) and
return the existing fallback string ("Sorry, I cannot think of a reply for
that."). `server.py`'s `/api/chat` route needs no changes — it already
treats `chatbot_query`'s return value as opaque text.

## Config, dependencies & deployment

- `requirements.txt`: add `anthropic` and `python-dotenv` (python-dotenv is
  not currently a Chatbot dependency).
- `.gitignore`: add `.env` — not currently listed, and this feature
  introduces the project's first real secret.
- New `.env.example` with `ANTHROPIC_API_KEY=` documenting the required
  variable, without a real key.
- `README.md`: update the "powered by Google Search" framing (already
  inaccurate before this change) to describe the small-talk/calculator/
  Claude flow; add setup steps for obtaining a key at console.anthropic.com
  and setting `ANTHROPIC_API_KEY` locally (`.env`) and in each deployment
  target already documented (Heroku, Railway, Render, Docker).

## Testing

No existing automated test suite in this repo — verify manually:

1. Small talk ("hello") and arithmetic ("2 + 2") still answer instantly with
   no API call.
2. A general-knowledge question (e.g. "What is the capital of France?")
   returns a Claude-generated answer via `curl localhost:8080/api/chat`.
3. An invalid/missing `ANTHROPIC_API_KEY` produces the fallback message via
   the API route, not a 500.

import ast
import operator
import os
import re

import requests
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

_GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

load_dotenv()


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


def _query_gemini(query):
    api_key = os.environ.get("GEMINI_API_KEY", "")
    response = requests.post(
        _GEMINI_API_URL,
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": query}]}],
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "generationConfig": {"maxOutputTokens": 300},
        },
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


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
        return _query_gemini(query)
    except requests.exceptions.HTTPError as e:
        print(f"answer_engine error (status): {e}")
        return fallback
    except requests.exceptions.RequestException as e:
        print(f"answer_engine error (connection): {e}")
        return fallback
    except Exception as e:
        print(f"answer_engine error: {e}")
        return fallback

import ast
import operator
import re
import requests

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_QUESTION_PREFIXES = (
    "what is a ", "what is an ", "what is ", "what's a ", "what's an ", "what's ",
    "who is ", "who's ", "define ",
)

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


def _simplify_question(query):
    lowered = query.strip().rstrip('?').lower()
    for prefix in _QUESTION_PREFIXES:
        if lowered.startswith(prefix):
            return lowered[len(prefix):].strip()
    return query.strip().rstrip('?')


def _query_duckduckgo(search_term):
    response = requests.get(
        'https://api.duckduckgo.com/',
        params={
            'q': search_term,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1,
        },
        headers={
            'User-Agent': 'Mozilla/5.0 (compatible; AIChatBot/1.0)',
        },
        timeout=5,
    )
    response.raise_for_status()
    data = response.json()

    for field in ('Answer', 'AbstractText', 'Definition'):
        text = data.get(field, '').strip()
        if text:
            return text

    for topic in data.get('RelatedTopics', []):
        text = topic.get('Text', '').strip()
        if text:
            return text

    return None


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

    raw_query = query.strip().rstrip('?')
    simplified_query = _simplify_question(query)

    for search_term in dict.fromkeys([simplified_query, raw_query]):
        if not search_term:
            continue
        try:
            text = _query_duckduckgo(search_term)
            if text:
                return text
        except Exception as e:
            print(f"google_search error: {e}")

    return fallback


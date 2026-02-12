import json
import requests

from app.doctor import run_doctor
from app.config import API_KEY
from app.ui import (
    user_input,
    info,
    error,
    show_help,
    stream_ai_response,
    typing_indicator,
)

API_URL = "https://api.openai.com/v1/responses"
MODEL = "gpt-4o-mini"
MAX_HISTORY = 10

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a helpful AI assistant running in a Linux terminal. "
        "You are allowed to use web search tools when needed to answer "
        "questions about current events, sports results, or recent news."
    ),
}


def _to_responses_input(messages):
    """
    Responses API input MUST NOT include assistant messages.
    Only system + user messages are allowed.
    """
    converted = []

    for msg in messages:
        if msg["role"] in ("system", "user"):
            converted.append(
                {
                    "role": msg["role"],
                    "content": [
                        {
                            "type": "input_text",
                            "text": msg["content"],
                        }
                    ],
                }
            )

    return converted

def _iter_response_text(response):
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue

        if line.startswith("data: "):
            data = line[len("data: ") :].strip()
        else:
            continue

        if data == "[DONE]":
            break

        try:
            event = json.loads(data)
        except json.JSONDecodeError:
            continue

        # Responses API streaming deltas
        if isinstance(event, dict):
            if isinstance(event.get("delta"), str):
                yield event["delta"]
                continue

            event_type = event.get("type", "")
            if event_type.endswith(".delta"):
                if isinstance(event.get("text"), str):
                    yield event["text"]
                    continue

def start_chat():
    info("Connected to OpenAI (Responses API + Web Search) ✅\n")

    # Conversation memory
    messages = [SYSTEM_PROMPT.copy()]

    while True:
        try:
            user_text = user_input().strip()
        except (KeyboardInterrupt, EOFError):
            info("\nGoodbye 👋")
            break

        # ---- COMMANDS ----
        if user_text.lower() in ("exit", "quit"):
            info("Goodbye 👋")
            break

        if user_text.lower() == "/clear":
            messages = [SYSTEM_PROMPT.copy()]
            info("🧹 Conversation cleared.")
            continue

        if user_text.lower() == "/help":
            show_help()
            continue

        if user_text.lower() == "/doctor":
            run_doctor()
            continue

        # ---- NORMAL CHAT ----
        messages.append({"role": "user", "content": user_text})

        # Trim history (keep system + last N turns)
        if len(messages) > 1 + MAX_HISTORY * 2:
            messages = [messages[0]] + messages[-MAX_HISTORY * 2 :]

        payload = {
            "model": MODEL,
            "input": _to_responses_input(messages),
            "tools": [
                {"type": "web_search"}
            ],
            "stream": True,
        }

        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                stream=True,
                timeout=60,
            )
            response.raise_for_status()

            status = typing_indicator()
            try:
                reply = stream_ai_response(
                    _iter_response_text(response),
                    on_first_chunk=status.stop,
                ).strip()
            finally:
                status.stop()

            if reply:
                messages.append({"role": "assistant", "content": reply})
            else:
                error("⚠️ The model returned no visible text.")

        except requests.exceptions.HTTPError:
            error("OpenAI API error")
            error(response.text)

        except requests.exceptions.RequestException:
            error("Network error — check your connection.")

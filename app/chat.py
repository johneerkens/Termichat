import json
import requests

from app.config import API_KEY
from app.ui import (
    user_input,
    info,
    error,
    show_help,
    stream_ai_response,
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
    return [
        {
            "role": msg["role"],
            "content": [
                {
                    "type": "input_text",
                    "text": msg["content"]
                }
            ],
        }
        for msg in messages
    ]

def start_chat():
    info("Connected to OpenAI (Responses API + Web Search) ✅\n")

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

        # ---- NORMAL CHAT ----
        messages.append({"role": "user", "content": user_text})

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
                timeout=30,
            )
            response.raise_for_status()

            def stream_chunks():
                for line in response.iter_lines():
                    if not line:
                        continue

                    if not line.startswith(b"data: "):
                        continue

                    data = line[len(b"data: "):]

                    if data == b"[DONE]":
                        break

                    try:
                        event = json.loads(data.decode("utf-8"))

                        # Stream final text output
                        for item in event.get("output", []):
                            if item.get("type") in ("output_text", "summary_text"):
                                yield item.get("text")

                    except Exception:
                        continue

            reply = stream_ai_response(stream_chunks())
            messages.append({"role": "assistant", "content": reply})

        except requests.exceptions.HTTPError:
            error("OpenAI API error")
            error(response.text)

        except requests.exceptions.RequestException:
            error("Network error — check your connection.")

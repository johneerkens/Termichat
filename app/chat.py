import requests

from app.doctor import run_doctor
from app.config import API_KEY
from app.ui import (
    user_input,
    ai_response,
    info,
    error,
    show_help,
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
            "stream": False,  # 🔴 DISABLED ON PURPOSE (STABILITY)
        }

        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            # ---- Extract assistant text (official & stable) ----
            reply_parts = []

            for item in data.get("output", []):
                if item.get("role") == "assistant":
                    for content in item.get("content", []):
                        if content.get("type") in ("output_text", "summary_text"):
                            reply_parts.append(content.get("text", ""))

            reply = "\n".join(reply_parts).strip()

            if reply:
                ai_response(reply)
                messages.append({"role": "assistant", "content": reply})
            else:
                error("⚠️ The model returned no visible text.")

        except requests.exceptions.HTTPError:
            error("OpenAI API error")
            error(response.text)

        except requests.exceptions.RequestException:
            error("Network error — check your connection.")


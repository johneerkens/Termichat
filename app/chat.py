import requests
import json
from app.config import API_KEY
from app.ui import user_input, ai_response, info, error, show_help, thinking, stream_ai_response

API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-4o-mini"
MAX_HISTORY = 10

SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are a helpful AI assistant running in a Linux terminal."
}

def start_chat():
    info("Connected to OpenAI ✅\n")

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
    "messages": messages,
    "temperature": 0.7
}

try:
    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={**payload, "stream": True},
        stream=True,
        timeout=30
    )
    response.raise_for_status()

    def stream_chunks():
        for line in response.iter_lines():
            if not line:
                continue

            if line.startswith(b"data: "):
                data = line[len(b"data: "):]

                if data == b"[DONE]":
                    break

                try:
                    chunk = json.loads(data.decode("utf-8"))
                    delta = chunk["choices"][0]["delta"]
                    if "content" in delta:
                        yield delta["content"]
                except Exception:
                    continue

    reply = stream_ai_response(stream_chunks())

    messages.append({"role": "assistant", "content": reply})

except requests.exceptions.HTTPError:
    error("OpenAI API error")
    error(response.text)

except requests.exceptions.RequestException:
    error("Network error — check your connection.")



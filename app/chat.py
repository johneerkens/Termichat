import requests
from app.config import API_KEY

API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-4o-mini"  # fast, cheap, great for terminal use

def start_chat():
    print("Connected to OpenAI ✅\n")

    while True:
        user_input = input("You > ")

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye 👋")
            break

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant in a Linux terminal."},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()
            reply = data["choices"][0]["message"]["content"]

            print(f"AI  > {reply}\n")

        except requests.exceptions.HTTPError as e:
            print("❌ OpenAI API error")
            print(response.text)

        except requests.exceptions.RequestException:
            print("❌ Network error. Check your connection.")

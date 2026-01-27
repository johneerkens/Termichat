import requests
from config import API_KEY, API_URL

def start_chat():
    while True:
        user_input = input("You > ")

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye 👋")
            break

        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "message": user_input
            }
        )

        if response.status_code == 200:
            print("AI  >", response.json().get("reply", "No response"))
        else:
            print("⚠️  Error communicating with AI API")

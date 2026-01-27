import os
import sys

API_KEY = os.getenv("TERMI_API_KEY")
API_URL = "https://api.example.com/chat"

if not API_KEY:
    print("❌ TERMI_API_KEY not set")
    print("Run: export TERMI_API_KEY='your_api_key'")
    sys.exit(1)

import os
import sys

API_KEY = os.getenv("TERMI_API_KEY")

if not API_KEY:
    print("❌ TERMI_API_KEY not set")
    print("Run:")
    print("export TERMI_API_KEY='sk-xxxxxxxxxxxxxxxx'")
    sys.exit(1)

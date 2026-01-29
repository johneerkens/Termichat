import os
import sys
import requests
import importlib.util
from pathlib import Path

from app.config import API_KEY
from app.ui import info, error

API_URL = "https://api.openai.com/v1/models"


def _check(label, ok, hint=None):
    if ok:
        info(f"✔ {label}")
        return True
    else:
        error(f"✖ {label}")
        if hint:
            info(f"  ↳ {hint}")
        return False


def run_doctor():
    info("\n🩺 TermiChat Doctor\n")

    healthy = True

    # Python version
    healthy &= _check(
        f"Python version: {sys.version.split()[0]}",
        sys.version_info >= (3, 8),
        "Python 3.8+ is required",
    )

    # API key
    healthy &= _check(
        "API key present",
        bool(API_KEY and API_KEY.startswith("sk-")),
        "Export TERMI_API_KEY=\"sk-...\"",
    )

    # API reachability (lightweight, no cost)
    try:
        r = requests.get(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=5,
        )
        healthy &= _check("OpenAI API reachable", r.status_code == 200)
    except Exception:
        healthy &= _check(
            "OpenAI API reachable",
            False,
            "Check internet connection or firewall",
        )

    # Dependencies
    for pkg in ("requests", "rich", "prompt_toolkit"):
        healthy &= _check(
            f"Dependency installed: {pkg}",
            importlib.util.find_spec(pkg) is not None,
            f"pipx reinstall termichat",
        )

    # pipx environment (heuristic)
    healthy &= _check(
        "pipx environment detected",
        "pipx" in sys.executable or ".local/share/pipx" in sys.executable,
        "Install using pipx for best results",
    )

    # Filesystem write access
    try:
        test_file = Path.home() / ".termichat_doctor_test"
        test_file.write_text("ok")
        test_file.unlink()
        healthy &= _check("Home directory writable", True)
    except Exception:
        healthy &= _check(
            "Home directory writable",
            False,
            "Check filesystem permissions",
        )

    if healthy:
        info("\nStatus: HEALTHY ✅\n")
    else:
        error("\nStatus: ISSUES FOUND ❌\n")
        info("Fix the issues above and re-run /doctor\n")

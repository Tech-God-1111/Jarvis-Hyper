#!/usr/bin/env python3
"""
JARVIS-HYPER Model Tester
Checks whether each Nemotron model in the failover chain is alive.

Run: python test-models.py
"""

import os
import sys
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv


# ============================================================
# CONFIG
# ============================================================
ROOT_DIR = Path(__file__).parent
BACKEND_DIR = ROOT_DIR / "backend"

# Load .env from backend
load_dotenv(BACKEND_DIR / ".env")

API_KEY = os.getenv("NVIDIA_API_KEY")
BASE_URL = "https://integrate.api.nvidia.com/v1"

# The model chain — mirrors what's in backend/core/config.py
MODELS = [
    {
        "tier": 1,
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "desc": "Ultra 550B — primary",
    },
    {
        "tier": 2,
        "model": "nvidia/nemotron-3-super-120b-a12b",
        "desc": "Super 120B — secondary",
    },
    {
        "tier": 3,
        "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
        "desc": "Nano 30B — fallback",
    },
]

TEST_PROMPT = "Reply with exactly three words: 'Systems are online'"


# ============================================================
# COLORS
# ============================================================
class C:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header():
    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════════════╗
║     JARVIS-HYPER // MODEL HEALTH CHECK                       ║
╚══════════════════════════════════════════════════════════════╝{C.END}
""")


# ============================================================
# TEST ONE MODEL
# ============================================================
def test_model(client: OpenAI, model: str, timeout: int = 30) -> dict:
    """Test a single model. Returns status dict."""
    result = {
        "model": model,
        "status": "unknown",
        "time": 0.0,
        "response": "",
        "error": "",
    }

    start = time.time()
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": TEST_PROMPT}],
            temperature=0.3,
            top_p=0.9,
            max_tokens=50,
            stream=False,
            timeout=timeout,
        )
        elapsed = time.time() - start

        content = completion.choices[0].message.content or ""
        # Strip reasoning content if present
        content = content.strip()

        result["status"] = "alive"
        result["time"] = elapsed
        result["response"] = content[:100]

    except Exception as e:
        elapsed = time.time() - start
        result["time"] = elapsed
        err_str = str(e)
        result["error"] = err_str[:200]

        # Classify the error
        if "410" in err_str or "Gone" in err_str or "end of life" in err_str:
            result["status"] = "eol"
        elif "overloaded" in err_str.lower() or "503" in err_str:
            result["status"] = "overloaded"
        elif "401" in err_str or "403" in err_str or "unauthorized" in err_str.lower():
            result["status"] = "auth_failed"
        elif "404" in err_str or "not found" in err_str.lower():
            result["status"] = "not_found"
        else:
            result["status"] = "error"

    return result


# ============================================================
# PRINT ONE RESULT
# ============================================================
def print_result(tier: int, desc: str, r: dict):
    status = r["status"]
    model = r["model"]
    elapsed = r["time"]

    if status == "alive":
        icon = f"{C.GREEN}✅ ALIVE{C.END}"
        detail = f"{elapsed:.2f}s | {C.GREEN}{r['response']}{C.END}"
    elif status == "eol":
        icon = f"{C.RED}❌ EOL{C.END}"
        detail = f"{C.RED}Model reached end-of-life on NVIDIA's servers{C.END}"
    elif status == "overloaded":
        icon = f"{C.YELLOW}⚠️  OVERLOADED{C.END}"
        detail = f"{C.YELLOW}Temporarily overloaded — retry later{C.END}"
    elif status == "not_found":
        icon = f"{C.RED}❌ NOT FOUND{C.END}"
        detail = f"{C.RED}Model name incorrect or removed{C.END}"
    elif status == "auth_failed":
        icon = f"{C.RED}🔑 AUTH FAILED{C.END}"
        detail = f"{C.RED}Check NVIDIA_API_KEY in backend/.env{C.END}"
    else:
        icon = f"{C.RED}❌ ERROR{C.END}"
        detail = f"{C.RED}{r['error']}{C.END}"

    print(f"  {C.BOLD}Tier {tier}{C.END} — {model}")
    print(f"         {desc}")
    print(f"         {icon}  {detail}")
    print()


# ============================================================
# MAIN
# ============================================================
def main():
    print_header()

    # Config check
    if not API_KEY:
        print(f"{C.RED}❌ NVIDIA_API_KEY not found in backend/.env{C.END}")
        sys.exit(1)

    masked = API_KEY[:12] + "..." + API_KEY[-4:] if len(API_KEY) > 16 else "***"
    print(f"{C.CYAN}API Key: {masked}{C.END}")
    print(f"{C.CYAN}Base URL: {BASE_URL}{C.END}")
    print(f"{C.CYAN}Testing {len(MODELS)} models...{C.END}")
    print()

    client = OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=30.0)

    results = []
    for entry in MODELS:
        tier = entry["tier"]
        model = entry["model"]
        desc = entry["desc"]

        print(f"{C.CYAN}→ Testing Tier {tier}...{C.END}")
        r = test_model(client, model)
        results.append((tier, desc, r))
        print_result(tier, desc, r)

    # ============================================================
    # SUMMARY TABLE
    # ============================================================
    print(f"{C.BOLD}══════════════════════════════════════════════════════════════{C.END}")
    print(f"{C.BOLD}  SUMMARY{C.END}")
    print(f"{C.BOLD}══════════════════════════════════════════════════════════════{C.END}")

    alive_count = 0
    for tier, desc, r in results:
        status = r["status"]
        model = r["model"]
        short = model.split("/")[-1][:40]

        if status == "alive":
            alive_count += 1
            print(f"  Tier {tier}  {C.GREEN}✅{C.END}  {short}  ({r['time']:.2f}s)")
        elif status == "eol":
            print(f"  Tier {tier}  {C.RED}❌{C.END}  {short}  (EOL)")
        elif status == "overloaded":
            print(f"  Tier {tier}  {C.YELLOW}⚠️{C.END}  {short}  (overloaded)")
        else:
            print(f"  Tier {tier}  {C.RED}❌{C.END}  {short}  ({status})")

    print()

    if alive_count == len(MODELS):
        print(f"{C.GREEN}{C.BOLD}🎉 All {alive_count}/{len(MODELS)} models alive!{C.END}")
    elif alive_count >= 1:
        print(f"{C.YELLOW}{C.BOLD}⚠️  {alive_count}/{len(MODELS)} models alive — failover will still work.{C.END}")
        print(f"{C.YELLOW}   Consider replacing dead tiers in backend/core/config.py{C.END}")
    else:
        print(f"{C.RED}{C.BOLD}❌ ALL MODELS DEAD — check your API key and model names.{C.END}")

    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Interrupted.{C.END}")
    except Exception as e:
        print(f"\n{C.RED}Fatal error: {e}{C.END}")
        sys.exit(1)
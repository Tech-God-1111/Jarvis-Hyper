#!/usr/bin/env python3
"""
JARVIS-HYPER Launcher
Starts the FastAPI backend (serves both HTML and API).
Run: python app-j.py
"""

import subprocess
import sys
import os
import time
import signal
import threading
import webbrowser
from pathlib import Path
import socket


# Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\033[97m'
    END = '\033[0m'


PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"

processes = []
shutting_down = False


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def print_header():
    local_ip = get_local_ip()
    print(f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║     JARVIS-HYPER // UNIFIED EDITION v3.0                     ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
    """)
    print(f"{Colors.GREEN}{Colors.BOLD}>> NETWORK MODE ENABLED{Colors.END}")
    print(f"{Colors.CYAN}PC IP: {Colors.BOLD}{local_ip}{Colors.END}")
    print(f"{Colors.CYAN}Login: {Colors.BOLD}http://{local_ip}:8000/{Colors.END}")
    print(f"{Colors.CYAN}Mega:  {Colors.BOLD}http://{local_ip}:8000/mega{Colors.END}")
    print("")


def print_status(message, status="INFO"):
    colors = {
        "INFO": Colors.CYAN,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "START": Colors.BLUE,
    }
    color = colors.get(status, Colors.WHITE)
    print(f"{color}[{status}]{Colors.END} {message}")


def check_dependencies():
    """Verify required packages are installed"""
    required = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("openai", "openai"),
        ("elevenlabs", "elevenlabs"),
        ("aiohttp", "aiohttp"),
        ("psutil", "psutil"),
        ("dotenv", "dotenv"),
    ]
    missing = []
    for package, import_name in required:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package)

    if missing:
        print_status(f"Installing missing packages: {', '.join(missing)}", "WARNING")
        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + missing,
            check=True,
        )


def run_backend():
    print_status("Starting JARVIS Backend...", "START")

    check_dependencies()

    local_ip = get_local_ip()
    print_status(f"Backend on http://{local_ip}:8000", "INFO")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    process = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn", "app:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000",
        ],
        cwd=str(BACKEND_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        encoding="utf-8",
        errors="replace",
    )
    return process


def open_browser():
    time.sleep(4)
    if not shutting_down:
        local_ip = get_local_ip()
        try:
            webbrowser.open(f"http://{local_ip}:8000/")
            print_status(f"Browser opened at http://{local_ip}:8000/", "SUCCESS")
        except Exception:
            pass


def handle_shutdown(signum=None, frame=None):
    global shutting_down
    if shutting_down:
        return
    shutting_down = True
    print_status("\nShutting down JARVIS-HYPER...", "WARNING")

    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=3)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass

    print_status("JARVIS-HYPER shut down", "SUCCESS")
    sys.exit(0)


def read_output(process, name, color):
    """Read subprocess output line-by-line. Never crashes on bad bytes."""
    try:
        for line in process.stdout:
            if not line:
                break
            line = line.rstrip()
            if not line:
                continue

            if "ERROR" in line or "error" in line.lower():
                print(f"{Colors.RED}[{name} ERROR]{Colors.END} {line}")
            elif "WARNING" in line or "warning" in line.lower():
                print(f"{Colors.YELLOW}[{name} WARN]{Colors.END} {line}")
            else:
                print(f"{color}[{name}]{Colors.END} {line}")
    except Exception as e:
        print(f"{Colors.RED}[{name} READER EXCEPTION]{Colors.END} {e}")


def main():
    try:
        print_header()
        print_status("Welcome to JARVIS-HYPER Launcher", "SUCCESS")
        print_status(f"Project: {PROJECT_ROOT}", "INFO")
        print("")

        local_ip = get_local_ip()
        print_status(f"Your IP: {local_ip}", "INFO")
        print_status(f"Access URL: http://{local_ip}:8000/", "SUCCESS")
        print("")
        print_status("Starting server...", "INFO")
        print("")

        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

        backend_process = run_backend()
        processes.append(backend_process)
        print_status("Backend started", "SUCCESS")

        print("")
        print_status("=" * 60, "INFO")
        print_status("JARVIS-HYPER is RUNNING!", "SUCCESS")
        print_status(f"Login:   http://localhost:8000/", "SUCCESS")
        print_status(f"Mega:    http://localhost:8000/mega", "SUCCESS")
        print_status(f"Network: http://{local_ip}:8000/", "SUCCESS")
        print_status(f"API:     http://{local_ip}:8000/api/", "SUCCESS")
        print_status(f"Docs:    http://{local_ip}:8000/docs", "SUCCESS")
        print_status("=" * 60, "INFO")
        print_status("Press Ctrl+C to stop", "WARNING")
        print("")

        threading.Thread(target=open_browser, daemon=True).start()

        threading.Thread(
            target=read_output,
            args=(backend_process, "BACKEND", Colors.GREEN),
            daemon=True,
        ).start()

        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                print_status("Backend crashed!", "ERROR")
                handle_shutdown()

    except KeyboardInterrupt:
        handle_shutdown()
    except Exception as e:
        print_status(f"Fatal error: {e}", "ERROR")
        handle_shutdown()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
JARVIS-HYPER Launcher - Network Edition
Starts both backend (FastAPI) and frontend (React) servers simultaneously.
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
import shutil
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
FRONTEND_DIR = PROJECT_ROOT / "frontend"

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
║     JARVIS-HYPER // NETWORK EDITION v2.0                     ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
    """)
    print(f"{Colors.GREEN}{Colors.BOLD}>> NETWORK MODE ENABLED{Colors.END}")
    print(f"{Colors.CYAN}PC IP: {Colors.BOLD}{local_ip}{Colors.END}")
    print(f"{Colors.CYAN}URL: {Colors.BOLD}http://{local_ip}:3000{Colors.END}")
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


def find_npm():
    npm_path = shutil.which("npm") or shutil.which("npm.cmd")
    if npm_path:
        return npm_path

    possible_paths = [
        r"D:\Program Files\nodejs\npm.cmd",
        r"C:\Program Files\nodejs\npm.cmd",
        r"C:\Program Files (x86)\nodejs\npm.cmd",
        os.path.expanduser(r"~\AppData\Roaming\npm\npm.cmd"),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return None


def check_and_install_dependencies():
    packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("openai", "openai"),
        ("elevenlabs", "elevenlabs"),
        ("aiohttp", "aiohttp"),
        ("psutil", "psutil"),
        ("python-dotenv", "dotenv"),
        ("python-multipart", "multipart"),
        ("httpx", "httpx"),
    ]
    for package, import_name in packages:
        try:
            __import__(import_name)
        except ImportError:
            print_status(f"Installing {package}...", "WARNING")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True,
            )


def run_backend():
    print_status("Starting JARVIS Backend...", "START")

    check_and_install_dependencies()

    local_ip = get_local_ip()
    print_status(f"Backend on http://{local_ip}:8000", "INFO")

    # Force UTF-8 IO for the subprocess
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app",
         "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(BACKEND_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        encoding="utf-8",       # <<<< THE FIX
        errors="replace",       # <<<< NEVER CRASH ON BAD BYTES
    )
    return process


def run_frontend():
    print_status("Starting JARVIS Frontend...", "START")

    npm_path = find_npm()
    if not npm_path:
        print_status("npm not found! Install Node.js from https://nodejs.org/", "ERROR")
        sys.exit(1)

    if not (FRONTEND_DIR / "node_modules").exists():
        print_status("Installing frontend dependencies (2-3 min)...", "WARNING")
        subprocess.run([npm_path, "install"], cwd=str(FRONTEND_DIR), check=True)

    local_ip = get_local_ip()
    print_status(f"Frontend on http://{local_ip}:3000", "INFO")

    env = os.environ.copy()
    env["HOST"] = "0.0.0.0"
    env["PORT"] = "3000"
    env["BROWSER"] = "none"

    process = subprocess.Popen(
        [npm_path, "start"],
        cwd=str(FRONTEND_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        encoding="utf-8",       # <<<< THE FIX
        errors="replace",       # <<<< NEVER CRASH ON BAD BYTES
    )
    return process


def open_browser():
    time.sleep(8)
    if not shutting_down:
        local_ip = get_local_ip()
        try:
            webbrowser.open(f"http://{local_ip}:3000")
            print_status(f"Browser opened at http://{local_ip}:3000", "SUCCESS")
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

            if "webpack" in line and "compiled" not in line:
                continue

            if "Compiled successfully" in line:
                print(f"{Colors.GREEN}[{name}]{Colors.END} {line}")
            elif "ERROR" in line or "error" in line.lower():
                print(f"{Colors.RED}[{name} ERROR]{Colors.END} {line}")
            elif "WARNING" in line or "warning" in line.lower():
                print(f"{Colors.YELLOW}[{name} WARN]{Colors.END} {line}")
            else:
                print(f"{color}[{name}]{Colors.END} {line}")
    except Exception as e:
        # Never let the reader thread die silently
        print(f"{Colors.RED}[{name} READER EXCEPTION]{Colors.END} {e}")


def main():
    try:
        print_header()
        print_status("Welcome to JARVIS-HYPER Launcher", "SUCCESS")
        print_status(f"Project: {PROJECT_ROOT}", "INFO")
        print("")

        local_ip = get_local_ip()
        print_status(f"Your IP: {local_ip}", "INFO")
        print_status(f"Access URL: http://{local_ip}:3000", "SUCCESS")
        print("")
        print_status("Starting servers...", "INFO")
        print("")

        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

        backend_process = run_backend()
        processes.append(backend_process)
        print_status("Backend started", "SUCCESS")
        time.sleep(2)

        frontend_process = run_frontend()
        processes.append(frontend_process)
        print_status("Frontend started", "SUCCESS")

        print("")
        print_status("=" * 60, "INFO")
        print_status("JARVIS-HYPER is RUNNING!", "SUCCESS")
        print_status(f"Local:   http://localhost:3000", "SUCCESS")
        print_status(f"Network: http://{local_ip}:3000", "SUCCESS")
        print_status(f"API:     http://{local_ip}:8000/api/", "SUCCESS")
        print_status("=" * 60, "INFO")
        print_status("Press Ctrl+C to stop", "WARNING")
        print("")

        threading.Thread(target=open_browser, daemon=True).start()

        threading.Thread(
            target=read_output,
            args=(backend_process, "BACKEND", Colors.GREEN),
            daemon=True,
        ).start()

        threading.Thread(
            target=read_output,
            args=(frontend_process, "FRONTEND", Colors.BLUE),
            daemon=True,
        ).start()

        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                print_status("Backend crashed!", "ERROR")
                handle_shutdown()
            if frontend_process.poll() is not None:
                print_status("Frontend crashed!", "ERROR")
                handle_shutdown()

    except KeyboardInterrupt:
        handle_shutdown()
    except Exception as e:
        print_status(f"Fatal error: {e}", "ERROR")
        handle_shutdown()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
JARVIS-HYPER Launcher
Production-ready FastAPI launcher.

Local:
    python app-j.py

Cloud:
    python app-j.py

The hosting platform must provide a PORT environment variable.
The FastAPI application serves both the frontend and API.
"""

import os
import sys
import signal
import subprocess
import socket
import time
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
BACKEND_APP = BACKEND_DIR / "app.py"

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))

IS_CLOUD = bool(
    os.environ.get("PORT")
    or os.environ.get("RENDER")
    or os.environ.get("RAILWAY_ENVIRONMENT")
)

process = None
shutting_down = False


# ============================================================
# LOGGING
# ============================================================

class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


def log(message, level="INFO"):
    colors = {
        "INFO": Colors.CYAN,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
    }

    color = colors.get(level, Colors.END)

    print(
        f"{color}[{level}]{Colors.END} {message}",
        flush=True,
    )


def print_header():
    print("=" * 60)
    print("             JARVIS-HYPER")
    print("              UNIFIED EDITION")
    print("=" * 60)

    if IS_CLOUD:
        log("Deployment mode: CLOUD", "SUCCESS")
    else:
        log("Deployment mode: LOCAL", "SUCCESS")

    log(f"Project: {PROJECT_ROOT}")
    log(f"Backend: {BACKEND_DIR}")
    log(f"Host: {HOST}")
    log(f"Port: {PORT}")

    print("=" * 60)


# ============================================================
# VALIDATION
# ============================================================

def validate_project():
    if not BACKEND_DIR.is_dir():
        raise FileNotFoundError(
            f"Backend directory not found: {BACKEND_DIR}"
        )

    if not BACKEND_APP.is_file():
        raise FileNotFoundError(
            f"FastAPI application not found: {BACKEND_APP}"
        )

    log("Project structure validated.", "SUCCESS")


def validate_dependencies():
    required = [
        "fastapi",
        "uvicorn",
    ]

    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        raise RuntimeError(
            "Missing dependencies: "
            + ", ".join(missing)
            + ". Install them using requirements.txt."
        )

    log("Required dependencies available.", "SUCCESS")


# ============================================================
# BACKEND STARTUP
# ============================================================

def start_backend():
    global process

    log("Starting FastAPI backend...", "INFO")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app:app",
        "--host",
        HOST,
        "--port",
        str(PORT),
    ]

    # Avoid development reload mode in production.
    if not IS_CLOUD:
        log("Local mode: automatic reload disabled.", "INFO")

    process = subprocess.Popen(
        command,
        cwd=str(BACKEND_DIR),
        env=env,
    )

    time.sleep(1)

    if process.poll() is not None:
        raise RuntimeError(
            f"Backend exited during startup. Exit code: {process.returncode}"
        )

    log("Backend process started.", "SUCCESS")


# ============================================================
# SHUTDOWN
# ============================================================

def shutdown(signum=None, frame=None):
    global shutting_down

    if shutting_down:
        return

    shutting_down = True

    log("Shutting down JARVIS-HYPER...", "WARNING")

    if process is not None and process.poll() is None:
        try:
            process.terminate()
            process.wait(timeout=10)

        except subprocess.TimeoutExpired:
            log("Backend did not stop gracefully. Forcing shutdown.", "WARNING")
            process.kill()
            process.wait()

        except Exception as exc:
            log(f"Shutdown error: {exc}", "ERROR")

    log("JARVIS-HYPER stopped.", "SUCCESS")


# ============================================================
# MAIN
# ============================================================

def main():
    print_header()

    validate_project()
    validate_dependencies()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        start_backend()

        print()
        log("JARVIS-HYPER IS RUNNING!", "SUCCESS")

        if IS_CLOUD:
            log(
                "Listening for incoming requests on the assigned cloud port.",
                "SUCCESS",
            )
        else:
            log(f"Login: http://localhost:{PORT}/", "SUCCESS")
            log(f"Mega:  http://localhost:{PORT}/mega", "SUCCESS")
            log(f"API:   http://localhost:{PORT}/api/", "SUCCESS")
            log(f"Docs:  http://localhost:{PORT}/docs", "SUCCESS")

        print()

        # Keep the launcher alive and monitor the backend.
        while not shutting_down:
            exit_code = process.poll()

            if exit_code is not None:
                log(
                    f"Backend exited unexpectedly. Exit code: {exit_code}",
                    "ERROR",
                )
                raise RuntimeError("FastAPI backend stopped.")

            time.sleep(2)

    except KeyboardInterrupt:
        log("Keyboard interrupt received.", "WARNING")

    finally:
        shutdown()


if __name__ == "__main__":
    try:
        main()

    except Exception as exc:
        log(f"Fatal launcher error: {type(exc).__name__}: {exc}", "ERROR")
        sys.exit(1)

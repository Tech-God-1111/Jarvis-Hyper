from fastapi import APIRouter
from pydantic import BaseModel
from core.data_collector import data_collector
import subprocess
import sys
import os
from pathlib import Path

router = APIRouter(prefix="/data", tags=["Data"])


# ============================================================
# APP LAUNCHER WHITELIST
# ============================================================
# Add more apps here. Key = what user says, Value = command to run
APP_WHITELIST = {
    "chrome":     "start chrome",
    "google":     "start chrome",
    "edge":       "start msedge",
    "microsoft edge": "start msedge",
    "notepad":    "start notepad",
    "calculator": "start calc",
    "calc":       "start calc",
    "explorer":   "start explorer",
    "file explorer": "start explorer",
    "task manager": "start taskmgr",
    "taskmgr":    "start taskmgr",
    "settings":   "start ms-settings:",
    "camera":     "start microsoft.windows.camera:",
    "war thunder": "start steam://rungameid/236390",   # War Thunder Steam ID
    "war thunder app": "start steam://rungameid/236390",
    "steam":      "start steam:",
}


class LaunchRequest(BaseModel):
    app: str


@router.post("/launch")
async def launch_app(req: LaunchRequest):
    """Launch an app from the whitelist"""
    app_key = req.app.lower().strip()

    # Find matching app
    command = APP_WHITELIST.get(app_key)

    # Partial match fallback
    if not command:
        for key, cmd in APP_WHITELIST.items():
            if key in app_key or app_key in key:
                command = cmd
                app_key = key
                break

    if not command:
        return {
            "success": False,
            "error": f"'{req.app}' is not in the whitelist, Sir.",
        }

    try:
        print(f"[LAUNCHER] Launching: {app_key} → {command}")

        # Windows: use shell=True with start command
        if sys.platform == "win32":
            subprocess.Popen(command, shell=True)
        elif sys.platform == "darwin":  # macOS
            app_name = app_key.replace("open ", "")
            subprocess.Popen(["open", "-a", app_name])
        else:  # Linux
            subprocess.Popen(command, shell=True)

        return {
            "success": True,
            "app": app_key,
            "message": f"Opening {app_key.title()}, Sir.",
        }
    except Exception as e:
        print(f"[LAUNCHER] Error: {e}")
        return {"success": False, "error": str(e)}


# ============================================================
# EXISTING ENDPOINTS
# ============================================================
@router.get("/weather")
async def get_weather(lat: float = 34.0522, lon: float = -118.2437):
    return await data_collector.fetch_weather(lat, lon)


@router.get("/news")
async def get_news(limit: int = 5):
    return {"news": await data_collector.fetch_news(limit)}


@router.get("/system")
async def get_system():
    return await data_collector.fetch_system_stats()


@router.get("/all")
async def get_all():
    return await data_collector.collect_all()
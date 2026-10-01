JARVIS-HYPER
============

A hyper-intelligent AI assistant with a British butler personality,
hyper-realistic voice output, and a Stark Industries HUD interface.

------------------------------------------------------------------------
FEATURES
------------------------------------------------------------------------

- Voice Recognition -- Speak naturally to JARVIS (Web Speech API)
- Hyper-realistic Voice -- High-quality TTS with British male accent
- Fast LLM Brain -- Low-latency AI model with thinking mode disabled
- System Telemetry -- Live CPU / Memory / Uptime stats
- File Analysis -- Drag & drop CSV, JSON, TXT, LOG, XML, YAML, MD
- Real-time Streaming -- See responses as they are generated
- Network Access -- Any device on your LAN can use JARVIS
- JARVIS Personality -- Dry British wit, "Sir" / "Boss" address

------------------------------------------------------------------------
TECH STACK
------------------------------------------------------------------------

Backend:
- FastAPI            -- Web framework
- Uvicorn            -- ASGI server
- OpenAI SDK         -- OpenAI-compatible client for any provider
- A TTS Provider     -- For hyper-realistic voice output
- Python 3.10+

Frontend:
- React 18
- Tailwind CSS
- Framer Motion
- Sonner             -- Toast notifications
- Web Speech API     -- Browser-native speech recognition

Optional:
- MongoDB            -- Chat history persistence (works without it too)

------------------------------------------------------------------------
PROJECT STRUCTURE
------------------------------------------------------------------------

jarvis-hyper/
|
+-- backend/
|   +-- app.py                  # FastAPI entry point
|   +-- requirements.txt
|   +-- .env                    # API keys (DO NOT COMMIT)
|   +-- core/
|   |   +-- __init__.py
|   |   +-- config.py           # Config loader
|   |   +-- ai.py               # LLM integration
|   |   +-- voice.py            # TTS integration
|   |   +-- data_collector.py   # System stats
|   +-- routes/
|       +-- __init__.py
|       +-- chat.py             # /api/chat/stream
|       +-- voice.py            # /api/voice/speak
|       +-- data.py             # /api/data/*
|
+-- frontend/
|   +-- package.json
|   +-- craco.config.js
|   +-- tailwind.config.js
|   +-- .env
|   +-- public/
|   |   +-- index.html
|   +-- src/
|       +-- index.js
|       +-- index.css
|       +-- App.js
|       +-- App.css
|       +-- pages/
|       |   +-- HyperPage.jsx
|       +-- components/
|       |   +-- Layout.jsx
|       |   +-- Telemetry.jsx
|       |   +-- ChatPanel.jsx
|       |   +-- DataPanel.jsx
|       |   +-- VoiceButton.jsx
|       +-- lib/
|           +-- api.js
|           +-- useVoice.js
|
+-- app-j.py                    # Launcher (starts both servers)
+-- README.md

------------------------------------------------------------------------
SETUP
------------------------------------------------------------------------

1. Clone the repo
   ----------------
   git clone https://github.com/Tech-God-1111/jarvis-hyper.git
   cd jarvis-hyper

2. Backend setup
   ----------------
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt

3. Frontend setup
   ----------------
   cd ../frontend
   npm install

4. Environment variables
   ------------------------
   Create backend/.env and add YOUR OWN API keys:

   # LLM Provider (any OpenAI-compatible API works)
   LLM_API_KEY=your-llm-api-key-here
   LLM_BASE_URL=https://your-llm-provider-url/v1
   LLM_MODEL=your-preferred-model-name

   # Text-to-Speech Provider
   TTS_API_KEY=your-tts-api-key-here
   TTS_VOICE_ID=your-preferred-voice-id
   TTS_MODEL=your-preferred-tts-model

   # Server
   PORT=8000
   CORS_ORIGINS="*"

   # Optional MongoDB
   MONGO_URL="mongodb://localhost:27017"
   DB_NAME="jarvis_db"

   Create frontend/.env:

   HOST=0.0.0.0
   PORT=3000
   WDS_SOCKET_HOST=0.0.0.0
   DANGEROUSLY_DISABLE_HOST_CHECK=true

5. Run JARVIS-HYPER
   ------------------
   cd jarvis-hyper
   python app-j.py

   This will:
   - Start the FastAPI backend on http://0.0.0.0:8000
   - Start the React frontend on http://0.0.0.0:3000
   - Auto-open the browser
   - Detect your LAN IP for network access
   - Show a pretty ASCII launcher banner

------------------------------------------------------------------------
ACCESS
------------------------------------------------------------------------

| Access Point                  | URL                            |
|-------------------------------|--------------------------------|
| Local (your PC)               | http://localhost:3000          |
| Network (any device on LAN)   | http://YOUR-LAN-IP:3000        |
| Backend API                   | http://YOUR-LAN-IP:8000/api/   |
| API Docs (Swagger)            | http://YOUR-LAN-IP:8000/docs   |

------------------------------------------------------------------------
USAGE
------------------------------------------------------------------------

Voice:
1. Click the MIC button
2. Speak: "Hello JARVIS" or "What's the status?"
3. JARVIS responds with voice

Text:
1. Type in the input field at the bottom
2. Press Enter or click SEND
3. Watch the streaming response

File Analysis:
1. Drag & drop a file (CSV, JSON, TXT, LOG, XML, YAML, MD)
2. Type your question about the file
3. JARVIS analyzes and responds

------------------------------------------------------------------------
API ENDPOINTS
------------------------------------------------------------------------

| Method | Endpoint           | Description                |
|--------|--------------------|----------------------------|
| POST   | /api/chat/stream   | Streaming chat response    |
| POST   | /api/chat/send     | Non-streaming chat         |
| POST   | /api/voice/speak   | Text-to-speech             |
| GET    | /api/data/system   | CPU, memory, disk stats    |
| GET    | /api/data/weather  | Weather (Lat/Lon based)    |
| GET    | /api/data/news     | News headlines             |
| GET    | /api/data/all      | All data at once           |
| GET    | /docs              | Swagger UI                 |

------------------------------------------------------------------------
THE JARVIS PERSONALITY
------------------------------------------------------------------------

Configured with a specific system prompt:
- British butler tone ("Sir" / "Boss")
- Dry, understated wit
- Short, punchy responses (optimized for voice)
- Stark Industries lab setting
- Calm, composed, unflappable

------------------------------------------------------------------------
KNOWN QUIRKS
------------------------------------------------------------------------

- Some reasoning models have thinking mode FORCED ON -- avoid these for
  voice chat (5+ minute waits per reply).
- Some reasoning models allow thinking to be DISABLED -- use these for
  instant replies.
- Diffusion-based text models are 100x+ slower for short replies --
  avoid them for voice assistants.
- Always test your chosen model with "Hello" before committing.

------------------------------------------------------------------------
TROUBLESHOOTING
------------------------------------------------------------------------

Frontend shows "Failed to fetch":
- Backend crashed -- check terminal for Python errors
- Wrong API key -- check backend/.env
- Model name wrong -- verify it matches your provider's catalog

Network access not working:
Run as Admin (Windows):
   New-NetFirewallRule -DisplayName "JARVIS-HYPER Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
   New-NetFirewallRule -DisplayName "JARVIS-HYPER Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
If still failing -- disable AP Isolation on your router.

Voice not working:
- Browser must support Web Speech API (Chrome/Edge work best)
- Microphone permission must be granted
- TTS API key must be valid and have credits

------------------------------------------------------------------------
LICENSE
------------------------------------------------------------------------

MIT

------------------------------------------------------------------------

Created by Moses A 
GitHub username (Tech-God-1111)
Stark Industries // JARVIS Division
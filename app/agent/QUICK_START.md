# Quick Start Guide - How to Talk to Your Agent

## ✅ Your Agent is Running!

Your agent worker is active and registered with LiveKit. Now you need to start the other services and create a session to connect.

## Step-by-Step Setup

### 1. Start the API Server (in a NEW terminal)

Open a **new PowerShell terminal** and run:

```powershell
cd app/api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv livekit
python main.py
```

Or if you already have the API dependencies installed:
```powershell
cd app/api
uvicorn main:app --reload --port 8000
```

**Keep this running** - this serves the web interface.

### 2. Start the Web Frontend (in ANOTHER terminal)

Open **another PowerShell terminal** and run:

```powershell
cd app/web
npm install  # Only first time
npm start
```

This will open your browser at `http://localhost:3000`

### 3. In Your Browser

1. **Go to** `http://localhost:3000`
2. **First, create an agent** (if none exist):
   - Click "Agents" tab
   - Click "Create Agent"
   - Fill in the form (agent name, system prompt, etc.)
   - Click "Create Agent"
3. **Start a call**:
   - Go to "Voice Call" tab
   - Select your agent
   - Click "🎤 Start Voice Call"
   - **Allow microphone permissions** when prompted
   - Start talking!

## Alternative: Direct API Call

If you want to test directly without the web UI:

```powershell
# Create a session (you'll need an agent ID first)
curl -X POST http://localhost:8000/sessions `
  -H "Content-Type: application/json" `
  -d '{"agent_id": "your-agent-id", "channel": "web"}'
```

But the web UI is easier! 😊

## Current Status

- ✅ **Agent Worker**: Running and registered
- ⚠️ **API Server**: Need to start (Step 1)
- ⚠️ **Web Frontend**: Need to start (Step 2)

## Troubleshooting

**"No agents available" error?**
- Go to Agents tab and create one first
- The agent configuration doesn't matter much since you're using the hardcoded simple agent

**"Failed to start call" error?**
- Make sure your agent worker terminal is still running
- Check that microphone permissions are enabled in your browser

**Agent not responding?**
- Check the agent worker terminal for errors
- Make sure the agent worker is still registered (should see heartbeat logs)

## What Happens When You Connect

1. Web UI creates a session via API
2. API creates a LiveKit room
3. Your browser connects to the room
4. Agent worker automatically joins the room
5. You can now speak and the agent responds!

---

**Tip**: Keep all three terminals open:
- Terminal 1: Agent worker (`python simple_agent.py dev`)
- Terminal 2: API server (`uvicorn main:app --reload`)
- Terminal 3: Web frontend (`npm start`)


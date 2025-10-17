# Quick Start Guide

Get up and running with BrainCX Voice SaaS in 15 minutes!

## Prerequisites

- Docker and Docker Compose installed
- API keys for:
  - LiveKit (sign up at https://cloud.livekit.io)
  - OpenAI (sign up at https://platform.openai.com)
  - Deepgram (sign up at https://console.deepgram.com)
  - ElevenLabs (sign up at https://elevenlabs.io)

## Step 1: Get API Keys (10 minutes)

### LiveKit Cloud (Free Tier)

1. Visit https://cloud.livekit.io
2. Sign up for a free account
3. Create a new project
4. Go to Settings → Keys
5. Copy:
   - LiveKit URL (e.g., `wss://your-project.livekit.cloud`)
   - API Key (e.g., `APIxxxxx`)
   - API Secret (e.g., `xxxxxxx`)

### OpenAI ($5 minimum)

1. Visit https://platform.openai.com
2. Sign up and add payment method
3. Go to API Keys
4. Create new secret key
5. Copy the key (starts with `sk-proj-`)

### Deepgram (Free $200 credit)

1. Visit https://console.deepgram.com
2. Sign up for free account
3. Go to API Keys
4. Create new key
5. Copy the key

### ElevenLabs (Free tier available)

1. Visit https://elevenlabs.io
2. Sign up for free account
3. Go to Profile → API Keys
4. Create new key
5. Copy the key

## Step 2: Configure Environment (2 minutes)

1. Navigate to the infra directory:
```bash
cd app/infra
```

2. Create a `.env` file based on `ENV_SETUP.md`:
```bash
# Copy this content to app/infra/.env

# Database
POSTGRES_USER=braincx
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=braincx
DATABASE_URL=postgresql://braincx:your_secure_password_here@db:5432/braincx

# LiveKit (from Step 1)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxx

# Authentication
ADMIN_PASSWORD=changeme
SESSION_SECRET=your-random-secret-key-min-32-characters

# OpenAI (from Step 1)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx

# Deepgram (from Step 1)
DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx

# ElevenLabs (from Step 1)
ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx

# Agent
AGENT_NAME=braincx-starter-agent
REACT_APP_API_URL=http://localhost:8000
```

3. Replace all the `xxxxxxxx` values with your actual API keys

## Step 3: Start the Platform (3 minutes)

1. Make sure you're in the `app/infra` directory

2. Start all services with Docker Compose:
```bash
docker compose up -d
```

3. Wait for services to start (about 1-2 minutes):
```bash
docker compose ps
```

You should see:
- ✓ db (PostgreSQL) - healthy
- ✓ api (FastAPI) - running
- ✓ agent (Voice agent) - running
- ✓ web (React) - running

4. Check logs if needed:
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f agent
```

## Step 4: Access the Platform

Open your browser and visit:

- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## Step 5: Create Your First Agent (2 minutes)

1. Go to http://localhost:3000/agents

2. Click **"Create Agent"**

3. Fill in the form:
   - **Name**: "My First Agent"
   - **System Prompt**: 
     ```
     You are a friendly and helpful voice assistant. 
     You can check the weather and perform calculations. 
     Always be polite and clear in your responses.
     ```
   - **Model**: gpt-4o-mini (recommended for starter)
   - **Temperature**: 0.7
   - Leave other fields as default

4. Click **"Create Agent"**

## Step 6: Make Your First Call! (1 minute)

1. Go to http://localhost:3000/call

2. Select "My First Agent" from the dropdown

3. Click **"Start Voice Call"**

4. Allow microphone access when prompted

5. Wait for connection (5-10 seconds)

6. Start talking! Try:
   - "Hello, how are you?"
   - "What's the weather in San Francisco?"
   - "What's 25 times 4?"

7. Click **"End Call"** when done

## Troubleshooting

### Issue: Services won't start

**Solution:**
```bash
# Stop all services
docker compose down

# Remove volumes (starts fresh)
docker compose down -v

# Start again
docker compose up -d
```

### Issue: "Failed to connect to API"

**Check:**
```bash
# Is the API running?
curl http://localhost:8000/health

# Check API logs
docker compose logs api
```

**Solution:** Make sure all environment variables are set correctly in `.env`

### Issue: "No agents available"

**Solution:** The database might not have initialized. Check:
```bash
# Check API logs
docker compose logs api

# Restart API to run migrations
docker compose restart api
```

### Issue: "Agent not connecting" or "No audio"

**Check:**
1. LiveKit credentials are correct in `.env`
2. Agent service is running: `docker compose ps agent`
3. Check agent logs: `docker compose logs agent`

**Solution:** 
```bash
# Restart agent service
docker compose restart agent
```

### Issue: "Microphone not working"

**Solution:**
- Use Chrome or Edge (best WebRTC support)
- Use `localhost` (HTTPS not required)
- Check browser microphone permissions
- Try with headphones to avoid echo

## Next Steps

Congratulations! You now have a working voice AI platform. 

### Learning Path

1. **Explore the UI** (15 minutes)
   - Create more agents with different prompts
   - View session history
   - Test different scenarios

2. **Customize Agents** (30 minutes)
   - Read [Agent Development Guide](AGENT_DEVELOPMENT.md)
   - Modify system prompts
   - Test different LLM models and temperatures

3. **Add Function Tools** (1 hour)
   - Read about function tools
   - Create custom functions
   - Integrate with external APIs

4. **Build Your Own Feature** (2+ hours)
   - Check [API Reference](API_REFERENCE.md)
   - Read [Architecture Guide](ARCHITECTURE.md)
   - Explore the codebase

### Useful Commands

```bash
# View logs
docker compose logs -f

# Restart a service
docker compose restart agent

# Stop all services
docker compose down

# Start all services
docker compose up -d

# Rebuild after code changes
docker compose up -d --build

# Clean everything (removes data!)
docker compose down -v
```

## Getting Help

- **Documentation**: Check the `docs/` folder
- **API Docs**: http://localhost:8000/docs
- **Logs**: `docker compose logs -f`

## What's Next?

- **Create specialized agents** for different use cases
- **Add custom function tools** for your business logic
- **Integrate with your systems** via webhooks and APIs
- **Deploy to production** when ready

Happy building! 🚀


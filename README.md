# BrainCX Voice SaaS - Starter Kit 🚀

Welcome to the **BrainCX Voice SaaS Starter Kit**! This is a simplified, educational version of the BrainCX Voice platform designed to help you learn and build AI-powered voice agents.

## 🎯 What is BrainCX Voice SaaS?

BrainCX Voice SaaS is a platform that enables you to build and deploy AI-powered voice agents that can:
- Handle phone calls (inbound and outbound)
- Engage in web-based voice conversations
- Integrate with external APIs and services
- Process and respond to natural language
- Provide real-time, intelligent voice interactions

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      BrainCX Voice SaaS                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │   Web    │  │   API    │  │  Agent  │  │  Database  │  │
│  │   (React)│◄─┤ (FastAPI)│◄─┤ (LiveKit)│  │ (PostgreSQL)│ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘ │
│                      │              │                        │
│                      ▼              ▼                        │
│              ┌───────────────────────────┐                   │
│              │    LiveKit Server         │                   │
│              │  (Real-time Voice Engine) │                   │
│              └───────────────────────────┘                   │
│                      │                                        │
│                      ▼                                        │
│              ┌───────────────────────────┐                   │
│              │  Telephony (Twilio/Telnyx)│                   │
│              │  + OpenAI + ElevenLabs    │                   │
│              └───────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### Components:

1. **Frontend (React)**: Web interface for managing agents and sessions
2. **Backend (FastAPI)**: REST API for managing agents, sessions, and integrations
3. **Agent (Python)**: Voice agent worker powered by LiveKit Agents framework
4. **Database (PostgreSQL)**: Stores agents, sessions, and configuration
5. **LiveKit Server**: Manages real-time voice/video connections
6. **External Services**: 
   - **OpenAI**: LLM for intelligent conversations
   - **Deepgram**: Speech-to-Text (STT)
   - **ElevenLabs**: Text-to-Speech (TTS)
   - **Twilio/Telnyx**: Telephony for phone calls

## 📋 Prerequisites

Before you begin, ensure you have:

- **Docker & Docker Compose** (recommended) OR individual installations below:
  - Python 3.10+
  - Node.js 18+
  - PostgreSQL 15+
- **API Keys** (you'll need to register for these services):
  - LiveKit Cloud account (or self-hosted LiveKit server)
  - OpenAI API key
  - Deepgram API key
  - ElevenLabs API key
  - Twilio or Telnyx account (for phone call functionality)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone the starter kit** (if you haven't already)

2. **Set up environment variables**:
   ```bash
   cd app/infra
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start all services**:
   ```bash
   docker compose up -d
   ```

4. **Access the application**:
   - Web UI: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Local Development

#### 1. Database Setup
```bash
# Start PostgreSQL (using Docker)
docker run -d \
  --name braincx-db \
  -e POSTGRES_USER=braincx \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=braincx \
  -p 5432:5432 \
  postgres:15
```

#### 2. Backend Setup
```bash
cd app/api
cp .env.example .env
# Edit .env and add your configuration

# Install dependencies
pip install -r requirements.txt

# Run migrations
python migrate.py

# Start the API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Agent Setup
```bash
cd app/agent
cp .env.example .env
# Edit .env and add your configuration

# Install dependencies
pip install -r requirements.txt

# Start the agent worker
python simple_agent.py dev
```

#### 4. Frontend Setup
```bash
cd app/web
cp .env.example .env
# Edit .env and add your configuration

# Install dependencies
npm install

# Start the development server
npm start
```

## 📚 Learning Path

We recommend following this learning path:

### 1. **Understand the Basics** (Week 1)
- Read through this README
- Review `docs/ARCHITECTURE.md`
- Set up the development environment
- Run the simple agent and test a web call

### 2. **Explore the Backend** (Week 2)
- Study `app/api/main.py` - REST API endpoints
- Study `app/api/models.py` - Database models
- Study `app/api/database.py` - Database connection
- Create your first agent via the API

### 3. **Understand Voice Agents** (Week 3)
- Study `app/agent/simple_agent.py` - Basic agent implementation
- Learn about LiveKit Agents framework
- Implement custom function tools
- Test voice interactions

### 4. **Frontend Development** (Week 4)
- Study `app/web/src/App.js` - Main application
- Study `app/web/src/components/` - React components
- Customize the UI
- Add new features

### 5. **Advanced Features** (Weeks 5-6)
- Study `docs/ADVANCED_FEATURES.md`
- Implement custom functions
- Add webhook integrations
- Implement phone call handling
- Build outbound calling features

## 🔑 Configuration

### Environment Variables

#### Backend (`app/api/.env`)
```env
# Database
DATABASE_URL=postgresql://braincx:yourpassword@db:5432/braincx

# LiveKit
LIVEKIT_URL=wss://your-livekit-instance.com
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Authentication
ADMIN_PASSWORD=changeme
SESSION_SECRET=your-secret-key-here

# External Services
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
ELEVENLABS_API_KEY=...

# Telephony (Optional)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TELNYX_API_KEY=...
```

#### Agent (`app/agent/.env`)
```env
# LiveKit
LIVEKIT_URL=wss://your-livekit-instance.com
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# External Services
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
ELEVENLABS_API_KEY=...

# Agent Configuration
AGENT_NAME=braincx-starter-agent
```

#### Frontend (`app/web/.env`)
```env
REACT_APP_API_URL=http://localhost:8000
```

## 📖 Key Concepts

### 1. **Agents**
Agents are the core of the system. Each agent has:
- A unique ID
- A name
- A system prompt (defines behavior)
- LLM configuration (model, temperature)
- Voice configuration (TTS voice ID, locale)

### 2. **Sessions**
Sessions represent active or completed conversations:
- Each session is linked to an agent
- Sessions can be web-based or phone-based
- Sessions track duration, cost, and status

### 3. **Function Tools**
Function tools allow agents to perform actions:
```python
@function_tool()
async def get_weather(
    self,
    context: RunContext,
    location: str
) -> str:
    """Get the current weather in a given location"""
    # Your implementation here
```

### 4. **LiveKit Rooms**
Each session creates a LiveKit room where:
- The agent connects as a participant
- Users connect via web or phone
- Real-time audio is processed

## 🛠️ Development Workflow

### Creating a New Agent

1. **Via API**:
```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom Agent",
    "system_prompt": "You are a helpful assistant that...",
    "llm_model": "gpt-4o-mini",
    "temperature": 0.7
  }'
```

2. **Via Web UI**:
   - Navigate to http://localhost:3000
   - Click "Agents" → "Create New Agent"
   - Fill in the details and save

### Testing Voice Calls

1. **Web Calls**:
   - Go to http://localhost:3000
   - Select an agent
   - Click "Start Call"
   - Allow microphone access

2. **Phone Calls** (requires Twilio/Telnyx setup):
   - Configure a phone number in the database
   - Link it to an agent
   - Call the number

## 🧪 Testing

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test agent creation
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Agent", "system_prompt": "You are helpful"}'
```

### Agent Testing
```bash
cd app/agent
python test_agent.py
```

## 📂 Project Structure

```
starter-kit-braincx-voice-saas/
├── app/
│   ├── api/               # Backend API (FastAPI)
│   │   ├── main.py        # Main API application
│   │   ├── models.py      # Database models
│   │   ├── database.py    # Database connection
│   │   ├── migrate.py     # Database migrations
│   │   └── requirements.txt
│   │
│   ├── agent/             # Voice agent workers
│   │   ├── simple_agent.py    # Basic agent implementation
│   │   └── requirements.txt
│   │
│   ├── web/               # Frontend (React)
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── App.js
│   │   │   └── index.js
│   │   ├── public/
│   │   └── package.json
│   │
│   └── infra/             # Infrastructure
│       ├── docker-compose.yml
│       ├── Dockerfile.api
│       ├── Dockerfile.agent
│       └── .env.example
│
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── AGENT_DEVELOPMENT.md
│   └── ADVANCED_FEATURES.md
│
└── README.md             # This file
```

## 🎓 Training Exercises

### Exercise 1: Create a Weather Agent
Create an agent that can check the weather in any city.

**Hints**:
- Use the OpenWeather API
- Implement a `get_weather` function tool
- Test with voice: "What's the weather in New York?"

### Exercise 2: Build a Calculator Agent
Create an agent that can perform mathematical calculations.

**Hints**:
- Implement function tools for add, subtract, multiply, divide
- Handle edge cases (division by zero)
- Test with voice: "What's 25 times 4?"

### Exercise 3: Database Integration
Create an agent that can query a database.

**Hints**:
- Add a simple table (e.g., products, customers)
- Implement a function tool to query the database
- Test with voice: "Find customer John Smith"

### Exercise 4: Custom UI Component
Build a custom React component for the frontend.

**Hints**:
- Create a session analytics dashboard
- Display call duration, cost, and status
- Add filtering and search

## 🆘 Troubleshooting

### Common Issues

#### 1. Agent Not Connecting
- **Check**: LiveKit credentials in `.env`
- **Check**: LiveKit server is running and accessible
- **Solution**: Verify LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET

#### 2. No Audio in Web Calls
- **Check**: Microphone permissions in browser
- **Check**: Browser console for errors
- **Solution**: Use HTTPS or localhost (required for microphone access)

#### 3. Database Connection Error
- **Check**: PostgreSQL is running
- **Check**: DATABASE_URL in `.env` is correct
- **Solution**: Verify credentials and host/port

#### 4. API Keys Not Working
- **Check**: Keys are correctly set in `.env` files
- **Check**: No extra spaces or quotes in `.env`
- **Solution**: Regenerate keys if needed

## 📞 Support & Resources

- **Documentation**: Check the `docs/` folder
- **LiveKit Documentation**: https://docs.livekit.io
- **OpenAI API**: https://platform.openai.com/docs
- **Deepgram**: https://developers.deepgram.com
- **ElevenLabs**: https://docs.elevenlabs.io

## 🎯 Next Steps

1. Complete the Quick Start setup
2. Follow the Learning Path
3. Complete the Training Exercises
4. Read the advanced documentation
5. Build your own custom agent!

## 📝 License

This starter kit is provided for educational purposes. Check with your organization for license details.

---

**Happy Coding! 🚀**

If you have questions or run into issues, refer to the documentation in the `docs/` folder or consult with your instructor.


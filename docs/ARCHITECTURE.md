# BrainCX Voice SaaS - Architecture Guide

## System Overview

BrainCX Voice SaaS is built on a microservices architecture with four main components:

1. **Web Frontend** (React)
2. **API Backend** (FastAPI)
3. **Voice Agent Workers** (LiveKit Agents)
4. **Database** (PostgreSQL)

## Detailed Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         User Interactions                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐                           ┌──────────────┐       │
│  │   Browser   │                           │   Phone      │       │
│  │  (Web User) │                           │   (Caller)   │       │
│  └──────┬──────┘                           └──────┬───────┘       │
│         │                                          │                │
│         │ WebSocket + WebRTC                       │ SIP/PSTN      │
│         │                                          │                │
└─────────┼──────────────────────────────────────────┼────────────────┘
          │                                          │
          │                                          │
┌─────────┼──────────────────────────────────────────┼────────────────┐
│         │              LiveKit Server              │                │
│         │                                          │                │
│  ┌──────▼────────┐                        ┌────────▼──────┐        │
│  │  WebRTC Room  │                        │  SIP Endpoint │        │
│  └──────┬────────┘                        └────────┬──────┘        │
│         │                                          │                │
│         └──────────────────┬───────────────────────┘                │
│                            │                                        │
└────────────────────────────┼────────────────────────────────────────┘
                             │
                             │ LiveKit Events & Media
                             │
┌────────────────────────────┼────────────────────────────────────────┐
│                            │      Application Layer                 │
├────────────────────────────┼────────────────────────────────────────┤
│                            │                                        │
│  ┌─────────────────────────▼──────────────────────────┐            │
│  │         Voice Agent Workers (Python)                │            │
│  │  ┌──────────────────────────────────────────────┐  │            │
│  │  │  Agent Logic (LiveKit Agents Framework)     │  │            │
│  │  │  - Speech-to-Text (Deepgram)                │  │            │
│  │  │  - LLM Processing (OpenAI)                  │  │            │
│  │  │  - Text-to-Speech (ElevenLabs)              │  │            │
│  │  │  - Function Tools (Custom Logic)            │  │            │
│  │  └──────────────────────────────────────────────┘  │            │
│  └───────────────────────┬──────────────────────────────┘          │
│                          │                                          │
│                          │ HTTP/REST API                            │
│                          │                                          │
│  ┌───────────────────────▼──────────────────────────┐              │
│  │       API Backend (FastAPI)                      │              │
│  │  - Agent Management                              │              │
│  │  - Session Tracking                              │              │
│  │  - Authentication                                │              │
│  │  - Database Operations                           │              │
│  │  - External Service Integration                  │              │
│  └───────────────────────┬──────────────────────────┘              │
│                          │                                          │
│                          │ SQL Queries                              │
│                          │                                          │
│  ┌───────────────────────▼──────────────────────────┐              │
│  │       PostgreSQL Database                        │              │
│  │  - Agents                                        │              │
│  │  - Sessions                                      │              │
│  │  - Organizations                                 │              │
│  │  - Phone Numbers                                 │              │
│  └──────────────────────────────────────────────────┘              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (React)

**Purpose**: User interface for managing agents and monitoring sessions

**Key Features**:
- Agent creation and configuration
- Real-time session monitoring
- Voice call interface (web-based)
- Session history and analytics

**Technology Stack**:
- React 18
- React Router (navigation)
- Axios (HTTP client)
- LiveKit React SDK (WebRTC)
- Tailwind CSS (styling)

**File Structure**:
```
app/web/src/
├── components/
│   ├── AgentManager.js      # Agent CRUD operations
│   ├── SessionsList.js      # Session monitoring
│   ├── UserSession.js       # Voice call interface
│   └── AdminLogin.js        # Authentication
├── App.js                   # Main application
├── api.js                   # API client
└── AuthContext.js           # Authentication context
```

### 2. Backend (FastAPI)

**Purpose**: REST API for managing system resources and business logic

**Key Responsibilities**:
- **Agent Management**: Create, read, update, delete agents
- **Session Management**: Track active and completed sessions
- **Authentication**: User and admin authentication
- **LiveKit Integration**: Create rooms, generate tokens
- **Telephony Integration**: Manage phone numbers, handle calls
- **Cost Tracking**: Calculate and store session costs

**API Endpoints**:
```
# Health Check
GET /health

# Authentication
POST /admin/login
POST /admin/logout

# Agents
GET /agents                # List all agents
POST /agents               # Create agent
GET /agents/{id}           # Get agent
PUT /agents/{id}           # Update agent
DELETE /agents/{id}        # Delete agent

# Sessions
POST /sessions             # Create session
GET /sessions              # List sessions
GET /sessions/{id}         # Get session
POST /sessions/{id}/end    # End session

# LiveKit
POST /token                # Generate room token

# Phone Management
GET /phone-numbers         # List phone numbers
POST /phone-numbers        # Add phone number
```

**Database Models**:
```python
class Organization(Base):
    id: UUID
    name: str
    created_at: datetime

class Agent(Base):
    id: UUID
    org_id: UUID
    name: str
    system_prompt: Text
    llm_model: str
    temperature: float
    locale: str
    elevenlabs_voice_id: str
    is_active: bool
    created_at: datetime

class Session(Base):
    id: UUID
    org_id: UUID
    agent_id: UUID
    room: str
    channel: ChannelType  # web, phone
    status: SessionStatus  # active, ended
    started_at: datetime
    ended_at: datetime (nullable)
    duration_seconds: float (nullable)
    cost_usd: float (nullable)
```

### 3. Voice Agent Workers

**Purpose**: Handle real-time voice interactions using AI

**How it Works**:

1. **Connection**: Agent connects to LiveKit server and listens for rooms
2. **Job Dispatch**: When a session is created, LiveKit dispatches a job to an agent
3. **Media Processing**:
   - **Input**: User speaks → Audio captured
   - **STT**: Audio → Text (via Deepgram)
   - **LLM**: Text → AI Response (via OpenAI)
   - **TTS**: Response → Audio (via ElevenLabs)
   - **Output**: Audio played to user
4. **Function Tools**: Agent can call custom functions during conversation
5. **Cleanup**: Session ends, agent disconnects

**Agent Lifecycle**:
```
┌─────────────────────────────────────────────────────────┐
│  Agent Entrypoint                                       │
│  └── Connect to room                                    │
│      └── Check for outbound call metadata               │
│          ├── Yes: Initiate SIP call                     │
│          └── No: Wait for inbound connection            │
│              └── Start agent session                    │
│                  ├── Load STT plugin (Deepgram)         │
│                  ├── Load LLM plugin (OpenAI)           │
│                  ├── Load TTS plugin (ElevenLabs)       │
│                  ├── Load VAD plugin (Silero)           │
│                  └── Register function tools            │
│                      └── Start conversation loop        │
│                          ├── Listen for user input      │
│                          ├── Process with LLM           │
│                          ├── Call functions if needed   │
│                          ├── Generate response          │
│                          └── Speak response             │
│                              └── Repeat until call ends │
└─────────────────────────────────────────────────────────┘
```

**Function Tools Example**:
```python
class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a helpful assistant..."
        )
    
    @function_tool()
    async def get_weather(
        self,
        context: RunContext,
        location: Annotated[str, "The city name"]
    ) -> str:
        """Get the current weather"""
        # Call weather API
        # Return result
        return f"Weather in {location}: Sunny, 75°F"
```

### 4. Database (PostgreSQL)

**Purpose**: Persistent storage for all system data

**Key Tables**:
- `orgs`: Organizations (multi-tenancy support)
- `users`: User accounts
- `agents`: AI agent configurations
- `sessions`: Call/conversation records
- `phone_numbers`: Phone number assignments

**Indexing Strategy**:
```sql
-- Fast lookups by agent
CREATE INDEX idx_sessions_agent_id ON sessions(agent_id);

-- Fast lookups by status
CREATE INDEX idx_sessions_status ON sessions(status);

-- Fast lookups by time
CREATE INDEX idx_sessions_started_at ON sessions(started_at DESC);
```

## Data Flow

### Inbound Phone Call Flow

```
1. User calls phone number
   ↓
2. Telephony provider (Twilio/Telnyx) receives call
   ↓
3. Telephony provider sends SIP invite to LiveKit
   ↓
4. LiveKit creates room and dispatches agent job
   ↓
5. Agent worker receives job, connects to room
   ↓
6. Agent queries API: "Which agent handles this phone number?"
   ↓
7. API returns agent configuration
   ↓
8. Agent initializes with configuration
   ↓
9. SIP call connects, audio streams start
   ↓
10. Agent greets user, conversation begins
    ↓
11. [Conversation Loop - see Agent Lifecycle]
    ↓
12. User hangs up OR agent ends call
    ↓
13. Agent reports session end to API
    ↓
14. API calculates cost, updates session status
    ↓
15. Agent disconnects, job completes
```

### Web Call Flow

```
1. User opens web UI, selects agent
   ↓
2. Frontend calls API: POST /sessions
   ↓
3. API creates session record
   ↓
4. API creates LiveKit room
   ↓
5. API generates user token
   ↓
6. API returns room info + token to frontend
   ↓
7. Frontend connects to LiveKit room
   ↓
8. LiveKit dispatches agent job
   ↓
9. Agent worker receives job, connects to room
   ↓
10. Agent queries API for agent configuration
    ↓
11. WebRTC audio connection established
    ↓
12. Agent greets user, conversation begins
    ↓
13. [Conversation Loop]
    ↓
14. User clicks "End Call" OR agent ends
    ↓
15. Frontend calls API: POST /sessions/{id}/end
    ↓
16. API updates session, calculates cost
    ↓
17. Agent and user disconnect
```

## External Service Integration

### OpenAI (LLM)
- **Purpose**: Natural language understanding and generation
- **Models**: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
- **Configuration**: Model, temperature, max tokens
- **Cost**: $0.15-$30 per million tokens

### Deepgram (STT)
- **Purpose**: Convert speech to text
- **Models**: nova-2, nova, base
- **Languages**: 30+ languages supported
- **Cost**: $0.0043 per minute

### ElevenLabs (TTS)
- **Purpose**: Convert text to speech
- **Voices**: 100+ pre-made voices
- **Custom Voices**: Clone voices
- **Cost**: $0.18 per 1000 characters

### LiveKit
- **Purpose**: Real-time WebRTC infrastructure
- **Features**: 
  - Rooms and participants
  - Agent dispatch
  - SIP connectivity
  - Recording
- **Deployment**: Cloud or self-hosted

### Twilio/Telnyx (Telephony)
- **Purpose**: Phone call connectivity
- **Features**:
  - Inbound/outbound calls
  - SIP trunking
  - Phone number provisioning
- **Cost**: ~$0.013 per minute

## Security Considerations

### Authentication
- Admin password for dashboard access
- Session-based authentication
- API key authentication for external integrations

### API Security
- CORS restrictions
- Rate limiting (recommended)
- Input validation
- SQL injection prevention (using SQLAlchemy ORM)

### Data Privacy
- Secure storage of API keys (environment variables)
- PII redaction options
- Session data encryption in transit (HTTPS/WSS)

### Network Security
- All services behind reverse proxy (Caddy)
- HTTPS/TLS for all external connections
- WebSocket Secure (WSS) for real-time audio

## Scalability

### Horizontal Scaling

**Agent Workers**: 
- Multiple agent containers can run simultaneously
- LiveKit automatically load-balances jobs
- Each worker can handle multiple sessions

**API Backend**:
- Stateless design allows easy horizontal scaling
- Add more API containers behind load balancer
- Use Redis for session storage (not in-memory)

**Database**:
- Use connection pooling
- Read replicas for analytics queries
- Partitioning for large session tables

### Performance Optimization

**Caching**:
- Cache agent configurations in memory
- Cache frequently accessed database queries
- Use CDN for static frontend assets

**Database Optimization**:
- Proper indexing on query columns
- Periodic cleanup of old sessions
- Archive old data to cold storage

**Agent Optimization**:
- Reuse HTTP connections to external services
- Stream responses from LLM (faster TTFB)
- Use faster STT/TTS models when appropriate

## Monitoring & Observability

### Metrics to Track

**System Health**:
- API response times
- Database connection pool status
- Agent worker uptime
- LiveKit room creation rate

**Business Metrics**:
- Active sessions
- Session duration
- Cost per session
- Agent utilization

**Quality Metrics**:
- Call drop rate
- Audio quality metrics
- STT/TTS latency
- LLM response time

### Logging

**Structured Logging**:
```python
logger.info("Session started", extra={
    "session_id": session.id,
    "agent_id": agent.id,
    "channel": "phone",
    "caller": "+1234567890"
})
```

**Log Levels**:
- DEBUG: Detailed troubleshooting
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Failures requiring attention
- CRITICAL: System failures

## Deployment

### Docker Compose (Development)

All services run on a single machine:
```yaml
services:
  db: postgres:15
  api: FastAPI application
  agent-web: Web call agent
  agent-phone: Phone call agent
  web: React frontend
  caddy: Reverse proxy
```

### Production Deployment

**Recommended Architecture**:
- Kubernetes cluster for orchestration
- Managed PostgreSQL (AWS RDS, GCP CloudSQL)
- Load balancer for API and frontend
- Auto-scaling agent workers
- Monitoring with Prometheus + Grafana

## Next Steps

- Read `API_REFERENCE.md` for detailed API documentation
- Read `AGENT_DEVELOPMENT.md` for agent development guide
- Read `ADVANCED_FEATURES.md` for advanced feature implementation

---

**Last Updated**: October 2025


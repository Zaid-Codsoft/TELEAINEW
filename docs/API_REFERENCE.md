# API Reference

Complete reference for the BrainCX Voice SaaS API.

**Base URL**: `http://localhost:8000` (development)

**Content-Type**: `application/json`

---

## Health Check

### GET /health

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "BrainCX Voice API",
  "version": "1.0.0"
}
```

---

## Authentication

### POST /admin/login

Login as administrator.

**Request Body:**
```json
{
  "password": "your_admin_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Logged in successfully"
}
```

**Cookies**: Sets `braincx_session` cookie

### POST /admin/logout

Logout current session.

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Agents

### GET /agents

List all agents in the organization.

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Customer Support Agent",
    "system_prompt": "You are a helpful assistant...",
    "llm_model": "gpt-4o-mini",
    "temperature": 0.7,
    "locale": "en-US",
    "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### POST /agents

Create a new agent.

**Request Body:**
```json
{
  "name": "Sales Agent",
  "system_prompt": "You are a helpful sales assistant...",
  "llm_model": "gpt-4o-mini",
  "temperature": 0.7,
  "locale": "en-US",
  "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM"
}
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "name": "Sales Agent",
  "system_prompt": "You are a helpful sales assistant...",
  "llm_model": "gpt-4o-mini",
  "temperature": 0.7,
  "locale": "en-US",
  "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",
  "is_active": true,
  "created_at": "2024-01-15T11:00:00Z"
}
```

### GET /agents/{agent_id}

Get a specific agent by ID.

**Response:** Same as individual agent object above

**Error Responses:**
- `404 Not Found`: Agent doesn't exist

### PUT /agents/{agent_id}

Update an agent. All fields are optional.

**Request Body:**
```json
{
  "name": "Updated Agent Name",
  "system_prompt": "New prompt...",
  "llm_model": "gpt-4o",
  "temperature": 0.5,
  "is_active": false
}
```

**Response:** Updated agent object

### DELETE /agents/{agent_id}

Delete an agent permanently.

**Response:**
```json
{
  "message": "Agent deleted successfully"
}
```

---

## Sessions

### POST /sessions

Create a new voice session.

**Request Body:**
```json
{
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "channel": "web"
}
```

**Fields:**
- `agent_id` (required): ID of the agent to use
- `channel` (optional): "web" or "phone", defaults to "web"

**Response:**
```json
{
  "session_id": "770e8400-e29b-41d4-a716-446655440000",
  "room": "braincx-12345678",
  "url": "wss://your-livekit-instance.livekit.cloud",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Fields:**
- `session_id`: Database session ID
- `room`: LiveKit room name
- `url`: LiveKit server URL
- `token`: JWT token for connecting to LiveKit

**Usage:**
```javascript
import { Room } from 'livekit-client';

const room = new Room();
await room.connect(url, token);
```

### GET /sessions

List recent sessions.

**Query Parameters:**
- `limit` (optional): Number of sessions to return (default: 50)

**Example:** `GET /sessions?limit=20`

**Response:**
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "agent_id": "550e8400-e29b-41d4-a716-446655440000",
    "agent_name": "Customer Support Agent",
    "room": "braincx-12345678",
    "channel": "web",
    "status": "ENDED",
    "started_at": "2024-01-15T10:30:00Z",
    "ended_at": "2024-01-15T10:35:00Z",
    "duration": 300
  }
]
```

**Status Values:**
- `ACTIVE`: Session in progress
- `ENDED`: Session completed normally
- `ABANDONED`: User disconnected without ending
- `ERROR`: Session ended due to error

### POST /sessions/{session_id}/end

End an active session.

**Response:**
```json
{
  "message": "Session ended successfully",
  "ended_at": "2024-01-15T10:35:00Z",
  "duration_seconds": 300
}
```

---

## LiveKit Integration

### POST /token

Generate a LiveKit access token (advanced usage).

**Request Body:**
```json
{
  "room": "my-room-name",
  "identity": "user-123"
}
```

**Response:**
```json
{
  "url": "wss://your-livekit-instance.livekit.cloud",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented in the starter kit. For production, implement rate limiting based on your needs.

---

## Example Usage

### Python

```python
import requests

API_URL = "http://localhost:8000"

# Create an agent
response = requests.post(
    f"{API_URL}/agents",
    json={
        "name": "Test Agent",
        "system_prompt": "You are helpful",
        "llm_model": "gpt-4o-mini"
    }
)
agent = response.json()
print(f"Created agent: {agent['id']}")

# Create a session
response = requests.post(
    f"{API_URL}/sessions",
    json={
        "agent_id": agent['id'],
        "channel": "web"
    }
)
session = response.json()
print(f"Session URL: {session['url']}")
print(f"Token: {session['token']}")
```

### JavaScript

```javascript
const API_URL = 'http://localhost:8000';

// Create an agent
const createAgent = async () => {
  const response = await fetch(`${API_URL}/agents`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: 'Test Agent',
      system_prompt: 'You are helpful',
      llm_model: 'gpt-4o-mini'
    })
  });
  
  const agent = await response.json();
  console.log('Created agent:', agent.id);
  return agent;
};

// Create a session
const createSession = async (agentId) => {
  const response = await fetch(`${API_URL}/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      agent_id: agentId,
      channel: 'web'
    })
  });
  
  const session = await response.json();
  console.log('Session created:', session.room);
  return session;
};
```

### cURL

```bash
# Create an agent
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent",
    "system_prompt": "You are helpful",
    "llm_model": "gpt-4o-mini"
  }'

# List agents
curl http://localhost:8000/agents

# Create a session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "550e8400-e29b-41d4-a716-446655440000",
    "channel": "web"
  }'
```

---

## Interactive Documentation

The API includes interactive documentation powered by FastAPI:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide a web interface to test all endpoints directly in your browser.

---

## Next Steps

- Read the [Agent Development Guide](AGENT_DEVELOPMENT.md)
- Explore [Advanced Features](ADVANCED_FEATURES.md)
- Check the [Architecture Guide](ARCHITECTURE.md)


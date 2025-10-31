"""
BrainCX Voice SaaS - API Backend
Simplified starter kit version
"""
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import uuid
import secrets
import traceback
import asyncio

from dotenv import load_dotenv
load_dotenv('.env.local')

# LiveKit SDK for agent dispatching
try:
    from livekit import api
    LIVEKIT_API_AVAILABLE = True
except ImportError:
    LIVEKIT_API_AVAILABLE = False
    print("WARNING: livekit-api not installed. Install with: pip install livekit-api")

# JWT for token generation
try:
    import jwt
    import time
    PYJWT_AVAILABLE = True
except ImportError:
    PYJWT_AVAILABLE = False
    print("WARNING: PyJWT not installed. Install it with: pip install pyjwt")

# Local imports
from database import get_db, check_database_connection
from models import Session as SessionModel, Agent, SessionStatus, ChannelType, Organization

# Initialize FastAPI app
app = FastAPI(
    title="BrainCX Voice API",
    description="API for managing voice AI agents and sessions",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],  # Allow specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# LiveKit configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# Authentication configuration
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SESSION_SECRET = os.getenv("SESSION_SECRET", "your-secret-key-here")

# In-memory session store (use Redis in production)
active_admin_sessions = {}

# ============================================
# Pydantic Models (Request/Response schemas)
# ============================================

class TokenRequest(BaseModel):
    room: str
    identity: str

class TokenResponse(BaseModel):
    url: str
    token: str

class CreateSessionRequest(BaseModel):
    agent_id: str
    channel: str = "web"  # web or phone

class CreateSessionResponse(BaseModel):
    session_id: str
    room: str
    url: str
    token: str

class LoginRequest(BaseModel):
    password: str

class AgentCreateRequest(BaseModel):
    name: str
    system_prompt: str

class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    llm_model: Optional[str] = None
    stt_model: Optional[str] = None
    tts_model: Optional[str] = None
    temperature: Optional[float] = None
    locale: Optional[str] = None
    is_active: Optional[bool] = None

class AgentResponse(BaseModel):
    id: str
    name: str
    system_prompt: str
    llm_model: str
    stt_model: str
    tts_model: str
    temperature: float
    locale: str
    is_active: bool
    created_at: datetime

class SessionResponse(BaseModel):
    id: str
    agent_id: str
    agent_name: str
    room: str
    channel: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration: Optional[int]  # in seconds

# ============================================
# Helper Functions
# ============================================

def verify_admin(request: Request):
    """Verify admin authentication"""
    session_id = request.cookies.get("braincx_session")
    if not session_id or session_id not in active_admin_sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return True

def get_org(db: Session) -> Organization:
    """Get the first organization (simplified for starter kit)"""
    org = db.query(Organization).first()
    if not org:
        raise HTTPException(status_code=500, detail="No organization found. Run migrate.py first.")
    return org

# ============================================
# Health Check
# ============================================

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "BrainCX Voice API",
        "version": "1.0.0"
    }

# ============================================
# Authentication Endpoints
# ============================================

@app.post("/admin/login")
def admin_login(request: LoginRequest, response: Response):
    """Admin login endpoint"""
    if request.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Create session
    session_id = secrets.token_urlsafe(32)
    active_admin_sessions[session_id] = {
        "created_at": datetime.utcnow()
    }
    
    # Set cookie
    response.set_cookie(
        key="braincx_session",
        value=session_id,
        httponly=True,
        max_age=86400,  # 24 hours
        samesite="lax"
    )
    
    return {"success": True, "message": "Logged in successfully"}

@app.post("/admin/logout")
def admin_logout(request: Request, response: Response):
    """Admin logout endpoint"""
    session_id = request.cookies.get("braincx_session")
    if session_id in active_admin_sessions:
        del active_admin_sessions[session_id]
    
    response.delete_cookie("braincx_session")
    return {"success": True, "message": "Logged out successfully"}

# ============================================
# Agent Management Endpoints
# ============================================

@app.get("/agents", response_model=List[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    """List all agents"""
    org = get_org(db)
    agents = db.query(Agent).filter(Agent.org_id == org.id).all()
    
    return [
        AgentResponse(
            id=str(agent.id),
            name=agent.name,
            system_prompt=agent.system_prompt,
            llm_model=agent.llm_model,
            stt_model=agent.stt_model,
            tts_model=agent.tts_model,
            temperature=agent.temperature,
            locale=agent.locale,
            is_active=agent.is_active,
            created_at=agent.created_at
        )
        for agent in agents
    ]

@app.post("/agents", response_model=AgentResponse)
def create_agent(
    request: AgentCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new agent"""
    org = get_org(db)
    
    # Create agent with simplified fields (only name and system_prompt)
    # All other fields use defaults from the model
    agent = Agent(
        id=uuid.uuid4(),
        org_id=org.id,
        name=request.name,
        system_prompt=request.system_prompt,
        # All other fields use database defaults:
        # llm_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0" (will be set via defaults)
        # stt_model="tiny"
        # tts_model="microsoft/speecht5_tts"
        # temperature=0.7
        # locale="en-US"
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return AgentResponse(
        id=str(agent.id),
        name=agent.name,
        system_prompt=agent.system_prompt,
        llm_model=agent.llm_model,
        stt_model=agent.stt_model,
        tts_model=agent.tts_model,
        temperature=agent.temperature,
        locale=agent.locale,
        is_active=agent.is_active,
        created_at=agent.created_at
    )

@app.get("/agents/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get a specific agent"""
    agent = db.query(Agent).filter(Agent.id == uuid.UUID(agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentResponse(
        id=str(agent.id),
        name=agent.name,
        system_prompt=agent.system_prompt,
        llm_model=agent.llm_model,
        stt_model=agent.stt_model,
        tts_model=agent.tts_model,
        temperature=agent.temperature,
        locale=agent.locale,
        is_active=agent.is_active,
        created_at=agent.created_at
    )

@app.put("/agents/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: str,
    request: AgentUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update an agent"""
    agent = db.query(Agent).filter(Agent.id == uuid.UUID(agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update fields if provided
    if request.name is not None:
        agent.name = request.name
    if request.system_prompt is not None:
        agent.system_prompt = request.system_prompt
    if request.llm_model is not None:
        agent.llm_model = request.llm_model
    if request.stt_model is not None:
        agent.stt_model = request.stt_model
    if request.tts_model is not None:
        agent.tts_model = request.tts_model
    if request.temperature is not None:
        agent.temperature = request.temperature
    if request.locale is not None:
        agent.locale = request.locale
    if request.is_active is not None:
        agent.is_active = request.is_active
    
    db.commit()
    db.refresh(agent)
    
    return AgentResponse(
        id=str(agent.id),
        name=agent.name,
        system_prompt=agent.system_prompt,
        llm_model=agent.llm_model,
        stt_model=agent.stt_model,
        tts_model=agent.tts_model,
        temperature=agent.temperature,
        locale=agent.locale,
        is_active=agent.is_active,
        created_at=agent.created_at
    )

@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Delete an agent"""
    agent = db.query(Agent).filter(Agent.id == uuid.UUID(agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent)
    db.commit()
    
    return {"message": "Agent deleted successfully"}

# ============================================
# Session Management Endpoints
# ============================================

@app.post("/sessions", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db)
):
    """Create a new voice session"""
    try:
        org = get_org(db)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting organization: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Database error while getting organization: {str(e)}. Make sure to run migrate.py first."
        )
    
    # Verify agent exists
    try:
        agent = db.query(Agent).filter(Agent.id == uuid.UUID(request.agent_id)).first()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid agent_id format: {str(e)}")
    except Exception as e:
        print(f"❌ Error querying agent: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Generate unique room name
    room_name = f"braincx-{uuid.uuid4()}"
    
    # Create session in database
    try:
        session = SessionModel(
            id=uuid.uuid4(),
            org_id=org.id,
            agent_id=agent.id,
            room=room_name,
            channel=ChannelType(request.channel),
            status=SessionStatus.ACTIVE,
            started_at=datetime.utcnow()
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating session: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")
    
    # Create LiveKit room and token
    if not all([LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
        raise HTTPException(
            status_code=500,
            detail="LiveKit not configured. Set LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET"
        )
    
    if not PYJWT_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="PyJWT required for token generation. Install with: pip install pyjwt"
        )
    
    # Generate access token manually
    import time
    now = int(time.time())
    user_id = f"user-{uuid.uuid4()}"
    
    token_data = {
        "iss": LIVEKIT_API_KEY,
        "sub": user_id,
        "name": "User",
        "exp": now + 3600,  # 1 hour expiry
        "video": {
            "room": room_name,
            "roomJoin": True,
            "canPublish": True,
            "canSubscribe": True,
        }
    }
    
    try:
        access_token = jwt.encode(token_data, LIVEKIT_API_SECRET, algorithm="HS256")
    except Exception as e:
        print(f"❌ Error generating token: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate token: {str(e)}")
    
    # Dispatch agent to the room
    if LIVEKIT_API_AVAILABLE:
        try:
            print(f"📤 Dispatching agent to room: {room_name}")
            livekit_api = api.LiveKitAPI(
                url=LIVEKIT_URL,
                api_key=LIVEKIT_API_KEY,
                api_secret=LIVEKIT_API_SECRET
            )
            
            # Create room with agent dispatch
            await livekit_api.room.create_room(
                api.CreateRoomRequest(
                    name=room_name
                )
            )
            print(f"✅ Room created: {room_name}")
            
            # Dispatch agent worker to the room
            await livekit_api.agent_dispatch.create_dispatch(
                api.CreateAgentDispatchRequest(
                    room=room_name,
                    agent_name="braincx-starter-agent"  # Must match the agent name in simple_agent.py
                )
            )
            print(f"✅ Agent dispatched to room: {room_name}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not dispatch agent: {e}")
            # Don't fail the request if dispatch fails
            traceback.print_exc()
    else:
        print("⚠️  LiveKit API not available - agent dispatch skipped")
    
    return CreateSessionResponse(
        session_id=str(session.id),
        room=room_name,
        url=LIVEKIT_URL,
        token=access_token
    )

@app.get("/sessions", response_model=List[SessionResponse])
def list_sessions(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List recent sessions"""
    org = get_org(db)
    
    sessions = (
        db.query(SessionModel, Agent.name)
        .join(Agent, SessionModel.agent_id == Agent.id)
        .filter(SessionModel.org_id == org.id)
        .order_by(desc(SessionModel.started_at))
        .limit(limit)
        .all()
    )
    
    results = []
    for session, agent_name in sessions:
        duration = None
        if session.ended_at:
            duration = int((session.ended_at - session.started_at).total_seconds())
        
        results.append(SessionResponse(
            id=str(session.id),
            agent_id=str(session.agent_id),
            agent_name=agent_name,
            room=session.room,
            channel=session.channel.value,
            status=session.status.value,
            started_at=session.started_at,
            ended_at=session.ended_at,
            duration=duration
        ))
    
    return results

@app.post("/sessions/{session_id}/end")
def end_session(session_id: str, db: Session = Depends(get_db)):
    """End a session"""
    session = db.query(SessionModel).filter(
        SessionModel.id == uuid.UUID(session_id)
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != SessionStatus.ACTIVE:
        return {"message": "Session already ended"}
    
    # Update session
    session.status = SessionStatus.ENDED
    session.ended_at = datetime.utcnow()
    session.duration_seconds = (session.ended_at - session.started_at).total_seconds()
    
    db.commit()
    
    return {
        "message": "Session ended successfully",
        "ended_at": session.ended_at,
        "duration_seconds": session.duration_seconds
    }

# ============================================
# LiveKit Token Generation
# ============================================

@app.post("/token", response_model=TokenResponse)
def generate_token(request: TokenRequest):
    """Generate LiveKit access token"""
    if not all([LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
        raise HTTPException(
            status_code=500,
            detail="LiveKit not configured"
        )
    
    if not PYJWT_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="PyJWT required for token generation"
        )
    
    now = int(time.time())
    
    token_data = {
        "iss": LIVEKIT_API_KEY,
        "sub": request.identity,
        "name": request.identity,
        "exp": now + 3600,
        "video": {
            "room": request.room,
            "roomJoin": True,
            "canPublish": True,
            "canSubscribe": True,
        }
    }
    
    access_token = jwt.encode(token_data, LIVEKIT_API_SECRET, algorithm="HS256")
    
    return TokenResponse(
        url=LIVEKIT_URL,
        token=access_token
    )

# ============================================
# Startup Event
# ============================================

@app.on_event("startup")
def startup_event():
    """Startup event - check database connection before accepting requests"""
    print("=" * 60)
    print("🚀 BrainCX Voice SaaS API - Starting...")
    print("=" * 60)
    
    # Check database connection before starting server
    try:
        check_database_connection()
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ Server startup ABORTED due to database connection failure")
        print("=" * 60)
        raise
    
    print("\n" + "=" * 60)
    print("✅ All checks passed!")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"❤️  Health: http://localhost:8000/health")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


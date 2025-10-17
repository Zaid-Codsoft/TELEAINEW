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

from dotenv import load_dotenv
load_dotenv('.env.local')

# LiveKit imports
from livekit import api as livekit_api

# Local imports
from database import get_db
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
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
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
    llm_model: str = "gpt-4o-mini"
    temperature: float = 0.7
    locale: str = "en-US"
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"

class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    llm_model: Optional[str] = None
    temperature: Optional[float] = None
    locale: Optional[str] = None
    elevenlabs_voice_id: Optional[str] = None
    is_active: Optional[bool] = None

class AgentResponse(BaseModel):
    id: str
    name: str
    system_prompt: str
    llm_model: str
    temperature: float
    locale: str
    elevenlabs_voice_id: str
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
            temperature=agent.temperature,
            locale=agent.locale,
            elevenlabs_voice_id=agent.elevenlabs_voice_id,
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
    
    agent = Agent(
        id=uuid.uuid4(),
        org_id=org.id,
        name=request.name,
        system_prompt=request.system_prompt,
        llm_model=request.llm_model,
        temperature=request.temperature,
        locale=request.locale,
        elevenlabs_voice_id=request.elevenlabs_voice_id,
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
        temperature=agent.temperature,
        locale=agent.locale,
        elevenlabs_voice_id=agent.elevenlabs_voice_id,
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
        temperature=agent.temperature,
        locale=agent.locale,
        elevenlabs_voice_id=agent.elevenlabs_voice_id,
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
    if request.temperature is not None:
        agent.temperature = request.temperature
    if request.locale is not None:
        agent.locale = request.locale
    if request.elevenlabs_voice_id is not None:
        agent.elevenlabs_voice_id = request.elevenlabs_voice_id
    if request.is_active is not None:
        agent.is_active = request.is_active
    
    db.commit()
    db.refresh(agent)
    
    return AgentResponse(
        id=str(agent.id),
        name=agent.name,
        system_prompt=agent.system_prompt,
        llm_model=agent.llm_model,
        temperature=agent.temperature,
        locale=agent.locale,
        elevenlabs_voice_id=agent.elevenlabs_voice_id,
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
def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db)
):
    """Create a new voice session"""
    org = get_org(db)
    
    # Verify agent exists
    agent = db.query(Agent).filter(Agent.id == uuid.UUID(request.agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Generate unique room name
    room_name = f"braincx-{uuid.uuid4()}"
    
    # Create session in database
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
    
    # Create LiveKit room and token
    if not all([LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
        raise HTTPException(
            status_code=500,
            detail="LiveKit not configured. Set LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET"
        )
    
    lk_api = livekit_api.LiveKitAPI(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    
    # Generate access token for user
    token = livekit_api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.with_identity(f"user-{uuid.uuid4()}")
    token.with_name("User")
    token.with_grants(livekit_api.VideoGrants(
        room_join=True,
        room=room_name,
    ))
    
    access_token = token.to_jwt()
    
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
    
    token = livekit_api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.with_identity(request.identity)
    token.with_name(request.identity)
    token.with_grants(livekit_api.VideoGrants(
        room_join=True,
        room=request.room,
    ))
    
    return TokenResponse(
        url=LIVEKIT_URL,
        token=token.to_jwt()
    )

# ============================================
# Startup Event
# ============================================

@app.on_event("startup")
def startup_event():
    """Print startup information"""
    print("=" * 60)
    print("🚀 BrainCX Voice SaaS API - Starting...")
    print("=" * 60)
    print(f"API Docs: http://localhost:8000/docs")
    print(f"Health: http://localhost:8000/health")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


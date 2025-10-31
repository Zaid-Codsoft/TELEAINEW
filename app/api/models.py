"""
Database models for BrainCX Voice SaaS
"""
from sqlalchemy import Column, String, DateTime, Float, Text, Enum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class ChannelType(str, enum.Enum):
    """Channel types for sessions"""
    WEB = "web"
    PHONE = "phone"

class SessionStatus(str, enum.Enum):
    """Status values for sessions"""
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"
    ABANDONED = "ABANDONED"
    ERROR = "ERROR"

class Organization(Base):
    """Organization/Tenant model for multi-tenancy"""
    __tablename__ = "orgs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("orgs.id"))
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Agent(Base):
    """AI Agent configuration model"""
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("orgs.id"))
    name = Column(String(255), nullable=False)
    system_prompt = Column(Text, nullable=False)
    # Model configurations (defaults match simple_agent.py)
    llm_model = Column(String(255), default="TinyLlama/TinyLlama-1.1B-Chat-v1.0")  # Local Hugging Face model
    stt_model = Column(String(50), default="tiny")  # Whisper model: tiny, base, small, medium, large
    tts_model = Column(String(255), default="microsoft/speecht5_tts")
    temperature = Column(Float, default=0.7)
    locale = Column(String(10), default="en-US")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Session(Base):
    """Session model for tracking conversations"""
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("orgs.id"))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    room = Column(String(255), nullable=False, unique=True)
    channel = Column(Enum(ChannelType), nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Cost tracking
    duration_seconds = Column(Float, nullable=True)
    cost_usd = Column(Float, nullable=True)
    
    # Phone call information
    caller_number = Column(String(20), nullable=True)
    called_number = Column(String(20), nullable=True)

class PhoneNumber(Base):
    """Phone number assignments to agents"""
    __tablename__ = "phone_numbers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("orgs.id"))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    e164 = Column(String(20), unique=True, nullable=False)  # +1234567890 format
    provider = Column(String(20), default="twilio")  # twilio or telnyx
    created_at = Column(DateTime, default=datetime.utcnow)


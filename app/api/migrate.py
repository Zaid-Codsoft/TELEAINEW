"""
Database migration script - creates all tables
"""
from database import engine
from models import Base, Organization, Agent
import uuid
from datetime import datetime

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully!")

def seed_data():
    """Create initial demo data"""
    from sqlalchemy.orm import Session
    
    print("\nSeeding initial data...")
    
    with Session(engine) as db:
        # Check if org already exists
        org = db.query(Organization).first()
        if org:
            print("✓ Data already exists, skipping seed")
            return
        
        # Create demo organization
        org = Organization(
            id=uuid.uuid4(),
            name="Demo Organization",
            created_at=datetime.utcnow()
        )
        db.add(org)
        db.flush()  # Get the org.id
        
        # Create demo agent
        agent = Agent(
            id=uuid.uuid4(),
            org_id=org.id,
            name="Demo Voice Assistant",
            system_prompt="You are a friendly and helpful voice assistant. You can help users with general questions and provide information. Always be polite, clear, and concise in your responses.",
            llm_model="gpt-4o-mini",
            temperature=0.7,
            locale="en-US",
            elevenlabs_voice_id="21m00Tcm4TlvDq8ikWAM",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(agent)
        
        # Commit all changes
        db.commit()
        
        print("✓ Created demo organization:", org.name)
        print("✓ Created demo agent:", agent.name)
        print(f"  Agent ID: {agent.id}")

if __name__ == "__main__":
    print("BrainCX Voice SaaS - Database Migration")
    print("=" * 50)
    
    try:
        create_tables()
        seed_data()
        print("\n" + "=" * 50)
        print("✓ Migration completed successfully!")
        print("\nYou can now start the API server:")
        print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()


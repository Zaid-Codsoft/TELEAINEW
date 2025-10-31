"""
Migration script to update agent model defaults
Updates existing agents to use new default model configurations
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db, engine
from models import Base, Agent
from sqlalchemy.orm import Session

def migrate_agents():
    """Update agent model defaults"""
    print("=" * 60)
    print("🔄 Migrating Agent Defaults...")
    print("=" * 60)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables verified")
    
    db = next(get_db())
    
    try:
        # Get all agents
        agents = db.query(Agent).all()
        print(f"Found {len(agents)} agents")
        
        updated_count = 0
        for agent in agents:
            # Update to new defaults if they have old defaults
            updated = False
            
            if agent.llm_model in ["mistralai/Mistral-7B-Instruct-v0.2", "gpt-4o-mini", "gemini-1.5-flash"]:
                agent.llm_model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
                updated = True
                print(f"  ✓ Updated agent '{agent.name}': LLM model -> TinyLlama/TinyLlama-1.1B-Chat-v1.0")
            
            if agent.stt_model == "base":
                agent.stt_model = "tiny"
                updated = True
                print(f"  ✓ Updated agent '{agent.name}': STT model -> tiny")
            
            if agent.tts_model in ["tts_models/en/ljspeech/glow-tts", "tts_models/en/ljspeech/speedy-speech"]:
                agent.tts_model = "microsoft/speecht5_tts"
                updated = True
                print(f"  ✓ Updated agent '{agent.name}': TTS model -> microsoft/speecht5_tts")
            
            if updated:
                updated_count += 1
        
        db.commit()
        
        print("=" * 60)
        if updated_count > 0:
            print(f"✅ Migration complete! Updated {updated_count} agent(s)")
        else:
            print("✅ Migration complete! No agents needed updating")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    exit(migrate_agents())


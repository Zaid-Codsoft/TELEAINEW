"""
Load seed data into TELEE database using Python
This script loads the dummy data from seed_data.sql
"""
import psycopg2
from dotenv import load_dotenv
import os
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load environment variables
load_dotenv(os.path.join(script_dir, '.env'))

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/TELEE')

def load_seed_data():
    """Load seed data from seed_data.sql"""
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("Reading seed_data_simple.sql...")
        seed_file = os.path.join(script_dir, 'seed_data_simple.sql')
        with open(seed_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("Executing seed data SQL...")
        cursor.execute(sql_content)
        conn.commit()
        
        print("\n[OK] Seed data loaded successfully!")
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM \"user\"")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM admin")
        admin_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM agent")
        agent_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dialogue")
        dialogue_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        kb_count = cursor.fetchone()[0]
        
        print(f"\nData Verification:")
        print(f"   Users: {user_count}")
        print(f"   Admins: {admin_count}")
        print(f"   Agents: {agent_count}")
        print(f"   Dialogues: {dialogue_count}")
        print(f"   Knowledge Base Articles: {kb_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\nError loading seed data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Loading Seed Data into TELEE Database")
    print("=" * 60)
    print()
    
    success = load_seed_data()
    
    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] Database setup complete!")
        print("=" * 60)
        print("\nConnection String:")
        print("  postgresql://postgres:postgres@localhost:5432/TELEE")
        print()
    else:
        print("\n" + "=" * 60)
        print("[FAILED] Setup failed. Check errors above.")
        print("=" * 60)


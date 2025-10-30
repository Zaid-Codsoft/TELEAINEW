"""
Database connection and session management
PostgreSQL only - requires DATABASE_URL environment variable
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

# Get database URL from environment - REQUIRED for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required!\n"
        "Set it in your .env.local file:\n"
        "DATABASE_URL=postgresql://user:password@localhost:5432/dbname\n"
        "\nExample for local PostgreSQL:\n"
        "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/braincx"
    )

# Validate that it's a PostgreSQL URL
if not DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+psycopg2://"):
    raise ValueError(
        f"Invalid DATABASE_URL: {DATABASE_URL}\n"
        "Must be a PostgreSQL connection string starting with 'postgresql://'"
    )

print(f"📦 Connecting to PostgreSQL database...")

# Create engine with connection pooling for PostgreSQL
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,        # Connection pool size
        max_overflow=20,     # Max overflow connections
        # PostgreSQL-specific connection args
        connect_args={
            "connect_timeout": 10,
        }
    )
    print("✅ PostgreSQL database engine created successfully")
except Exception as e:
    print(f"❌ Failed to create database engine: {e}")
    print("\nMake sure PostgreSQL is running and DATABASE_URL is correct.")
    raise

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency for FastAPI to get database session
    Usage in endpoints:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            # Use db here
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_database_connection():
    """
    Test database connection before server startup
    Raises an exception if connection fails
    """
    try:
        print("🔍 Checking database connection...")
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()  # Ensure query executes
        print("✅ Database connection verified successfully!")
        return True
    except Exception as e:
        print("❌ Database connection failed!")
        print(f"   Error: {str(e)}")
        print("\n   Troubleshooting:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Check that DATABASE_URL is correct in .env.local")
        print("   3. Verify database exists and credentials are valid")
        # Safely show partial URL without password
        try:
            url_part = DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else DATABASE_URL
            print(f"   4. Current DATABASE_URL: {url_part}@***")
        except:
            pass
        raise


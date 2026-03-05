"""Database configuration and session management for PostgreSQL"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Base class for models
Base = declarative_base()

# Global variables
engine = None
SessionLocal = None

def init_database():
    """Initialize database connection with error handling"""
    global engine, SessionLocal

    if not DATABASE_URL:
        print("⚠️  WARNING: DATABASE_URL not set. Database features disabled.")
        return False

    # Check if password placeholder is still there
    if "REPLACE_WITH_PASSWORD" in DATABASE_URL:
        print("⚠️  WARNING: DATABASE_URL contains placeholder password. Database features disabled.")
        print("   Set your Neon password in Render Dashboard to enable database.")
        return False

    try:
        # Create engine with connection pooling
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False,
            connect_args={"connect_timeout": 5}
        )

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # Session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        print("✅ Database connected successfully")
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   API will run without database features.")
        engine = None
        SessionLocal = None
        return False

# Initialize on import
DB_CONNECTED = init_database()


def get_db():
    """Dependency for FastAPI to get database session"""
    if not SessionLocal:
        raise Exception("Database not configured. Set DATABASE_URL environment variable.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def is_db_available():
    """Check if database is available"""
    return DB_CONNECTED and engine is not None

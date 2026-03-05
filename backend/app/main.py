from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, is_db_available
import os

# Import routes
if is_db_available():
    from app.api.routes import router
    print("✅ Using database-backed routes")
else:
    from app.api.routes_no_db import router_no_db as router
    print("⚠️  Using mock data routes (set DATABASE_URL for persistence)")

# Create database tables on startup (only if DB is available)
if engine is not None:
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
    except Exception as e:
        print(f"⚠️  Warning: Could not create tables: {e}")

app = FastAPI(
    title="Universe Migration Studio API",
    description="Backend API for Universe Migration Studio - Integrated Pipeline",
    version="1.1.0"
)

# Get frontend URL from environment or use defaults
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3001")
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    FRONTEND_URL,
    "https://migration-studio-pqor.onrender.com",  # Production frontend
    "https://migration-studio-api.onrender.com"  # API itself for health checks
]

# Remove duplicates and filter out None
allowed_origins = list(set([o for o in allowed_origins if o]))

print(f"🔒 CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(router)

@app.get("/")
async def root():
    db_status = "connected" if is_db_available() else "not_configured"
    return {
        "service": "Universe Migration Studio API",
        "version": "1.1.0",
        "status": "running",
        "pipeline": "integrated",
        "database": db_status
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "connected" if is_db_available() else "not_configured"
    }
# Force rebuild Thu Mar  5 06:57:24 CST 2026

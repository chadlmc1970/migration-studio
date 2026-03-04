from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.database import engine, Base
import os

# Create database tables on startup
Base.metadata.create_all(bind=engine)

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
    FRONTEND_URL
]

# Remove duplicates
allowed_origins = list(set(allowed_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {
        "service": "Universe Migration Studio API",
        "version": "1.1.0",
        "status": "running",
        "pipeline": "integrated"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

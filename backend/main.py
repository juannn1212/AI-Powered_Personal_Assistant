from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import os

from app.routes import auth, assistant, calendar, analytics, tasks, habits
from app.database import engine, Base
from app.config import settings
from app.models import User, Task, Habit, HabitLog

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 AI Personal Assistant Backend Starting...")
    yield
    # Shutdown
    print("👋 AI Personal Assistant Backend Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Personal Assistant API",
    description="Backend API for AI-powered personal assistant with ML capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["Assistant"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(habits.router, prefix="/api/habits", tags=["Habits"])

@app.get("/")
async def root():
    return {
        "message": "AI-Powered Personal Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-assistant-backend"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

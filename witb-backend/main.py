"""FastAPI application entry point following CLAUDE.md best practices."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine
from routes import players, tournaments


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup - Create all tables for local development
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    print("Database tables created successfully")
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="WITB API",
    description="What's In The Bag API for golf equipment tracking",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:3001"
    ).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(players.router)
app.include_router(tournaments.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "WITB API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
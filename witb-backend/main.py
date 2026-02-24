"""FastAPI application entry point following CLAUDE.md best practices."""

import logging
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.getLogger("apscheduler").setLevel(logging.INFO)

import models
from database import engine
from populate_ogwr_players import populate_ogwr_players
from routes import ebay, players, tournaments, user_bag, witb
from auth import routes as auth_routes

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup - Create all tables for local development
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    print("Database tables created successfully")

    # Schedule OGWR rankings update every Monday at 6am
    scheduler.add_job(
        populate_ogwr_players,
        "cron",
        day_of_week="mon",
        hour=6,
        minute=0,
        timezone="America/Los_Angeles",
    )
    scheduler.start()
    print("Scheduler started: OGWR rankings update every Monday at 6:00am")

    yield

    scheduler.shutdown()
    print("Scheduler stopped")


app = FastAPI(
    title="WITB API",
    description="What's In The Bag API for golf equipment tracking",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
    ).split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(ebay.router)
app.include_router(players.router)
app.include_router(tournaments.router)
app.include_router(user_bag.router)
app.include_router(witb.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "WITB API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

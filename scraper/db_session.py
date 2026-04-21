#!/usr/bin/env python3
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(Path(__file__).parent.parent / "witb-backend" / ".env")

_url = os.getenv("DATABASE_URL") or os.getenv("LOCAL_DATABASE_URL")

if not _url:
    raise RuntimeError("No DATABASE_URL configured. Set DATABASE_URL in witb-backend/.env")

# Convert async driver URLs to sync equivalents for CLI scripts
DATABASE_URL = (
    _url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        .replace("sqlite+aiosqlite://", "sqlite://")
)

if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

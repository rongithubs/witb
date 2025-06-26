from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Use DATABASE_URL from environment (Supabase), fallback to LOCAL_DATABASE_URL for local dev
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("LOCAL_DATABASE_URL")

# Configure engine based on database type
if DATABASE_URL and "sqlite" in DATABASE_URL:
    # SQLite configuration
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,  # Enable SQL logging for development
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL configuration (Supabase or local PostgreSQL)
    engine = create_async_engine(
        DATABASE_URL, 
        echo=False,
        connect_args={"statement_cache_size": 0}
    )
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

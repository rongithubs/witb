"""FastAPI dependencies following CLAUDE.md FA-3."""
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal


async def get_db() -> AsyncSession:
    """Database dependency."""
    async with SessionLocal() as session:
        yield session
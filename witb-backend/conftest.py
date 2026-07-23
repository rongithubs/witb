"""Pytest configuration and fixtures following CLAUDE.md T-8."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import models
from dependencies import get_db
from main import app

# Test database engine
test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Test database dependency."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)


@asynccontextmanager
async def _noop_lifespan(_app: object) -> AsyncGenerator[None, None]:
    """Replace the production lifespan during tests.

    The real lifespan runs `create_all` against the engine built from
    DATABASE_URL (Supabase) and starts the OGWR scheduler. Letting it run under
    TestClient points DDL at the production database and shares one asyncpg
    connection across per-test event loops, which fails with
    "another operation is in progress".
    """
    yield


@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> TestClient:
    """Create a test client with test database."""
    app.dependency_overrides[get_db] = lambda: db_session
    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = _noop_lifespan

    with TestClient(app) as test_client:
        yield test_client

    app.router.lifespan_context = original_lifespan
    app.dependency_overrides.clear()

import pytest
from app.main import app
from app.db import get_db, Base
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from collections.abc import AsyncGenerator
from httpx import ASGITransport, AsyncClient


TEST_DATABASE_URL="postgresql+psycopg://ecommerce_user:ecommerce@localhost/ecommerce_testing_db"

@pytest.fixture(scope="session")
def anyio_backend():
    return (
        "asyncio",
        {"loop_factory": asyncio.SelectorEventLoop},
    )

@pytest.fixture(scope="session")
def test_engine():
    engine= create_async_engine(
        url=TEST_DATABASE_URL,
        poolclass=NullPool
    )
    return engine

@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()

@pytest.fixture
async def db_session(test_engine, setup_database) -> AsyncGenerator[AsyncSession]:

    test_session_maker = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with test_session_maker() as session:
        yield session

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:

    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()




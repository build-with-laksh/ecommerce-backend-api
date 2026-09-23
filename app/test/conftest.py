import pytest
from app.main import app
from app.db import get_db, Base
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from collections.abc import AsyncGenerator
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from app import models


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

    conn = await test_engine.connect()
    trans = await conn.begin()

    test_session_maker = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint"
    )

    async with test_session_maker() as session:
        try:
            yield session
        finally:
            await trans.rollback()
            await conn.close()



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

@pytest.fixture
async def user(
    client
):
    response = await client.post(
        '/users/register',
        json={
            "username":"TestingUser",
            "email":"testinguser@gmail.com",
            "password":"testinguser@123"
        }
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture
async def token(
        client,
        user
) -> str:
    
    response = await client.post(
        '/users/login',
        data={
            "username":"TestingUser",
            "password":"testinguser@123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    return response.json()["access_token"]

@pytest.fixture
async def admin_token(
    client,
    db_session
) -> str:

    response = await client.post(
        '/users/register',
        json={
        "username":"Admin123",
        "email":"admin@gmail.com",
        "password":"Admin123"
        }
    )

    assert response.status_code == 200
    result = await db_session.execute(select(models.User).where(models.User.id == response.json()["id"]))
    user = result.scalars().first()

    user.is_admin = True
    await db_session.commit()

    response = await client.post(
        '/users/login',
        data={
            "username":"Admin123",
            "password":"Admin123"
        }
    )
    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
async def product(
    client,
    admin_token
) -> int:

    response = await client.post(
        '/products',
        json={
            "product_name":"Testing Product 2",
            "product_category":"Testing Category",
            "product_price":10000,
            "stock_quantity":1000
        },
        headers={
            "Authorization" : f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200
    return response.json()

@pytest.fixture
async def cart_item(
    client,
    product,
    token
):
    response = await client.post(
        '/cart',
        json={
            "product_id" : product["id"],
            "quantity" : 100
        },
        headers={
            "Authorization" : f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    return response.json()
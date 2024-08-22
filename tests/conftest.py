from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from database.config import TEST_DB
from database.schemas import Base
from database.my_engine import get_db
from sqlalchemy.pool import NullPool
from main import app
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi.testclient import TestClient
import asyncio


engine_test = create_async_engine(
    f'mysql+asyncmy://{TEST_DB.get("user")}:{TEST_DB.get("password")}@{TEST_DB.get("host")}/{TEST_DB.get("database")}',
    echo=TEST_DB.get('echo'),
    pool_recycle=3600,
    poolclass=NullPool
)

asyns_connection = sessionmaker(
    expire_on_commit=False,
    class_=AsyncSession,
    bind=engine_test,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with asyns_connection() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True, scope='session')
async def prepare_databse():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# @pytest.fixture(scope="session")
# def event_loop(request):
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


# ac = TestClient(app)


transport = ASGITransport(app=app)
@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
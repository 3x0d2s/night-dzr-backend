import asyncio
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.database import Base, get_db_session
from src.config import config
from src.main import app

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://{user_name}:{user_password}@{host}:{port}/{db_name}".format(
    user_name=config.POSTGRES_USERNAME,
    user_password=config.POSTGRES_PASSWORD.get_secret_value(),
    host=config.POSTGRES_HOST,
    port=config.POSTGRES_PORT,
    db_name=config.POSTGRES_DB_NAME_TEST
)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


async def override_get_db():
    async with AsyncSessionLocal() as async_session:
        yield async_session


app.dependency_overrides[get_db_session] = override_get_db


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

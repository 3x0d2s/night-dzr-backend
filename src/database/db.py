from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.config import config

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://{user_name}:{user_password}@{host}:{port}/{db_name}".format(
    user_name=config.POSTGRES_USERNAME,
    user_password=config.POSTGRES_PASSWORD.get_secret_value(),
    host=config.POSTGRES_HOST,
    port=config.POSTGRES_PORT,
    db_name=config.POSTGRES_DB_NAME
)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session

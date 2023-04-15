from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.security import security
from src.routers.users import users
from src.sql.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="NightDozor_Backend",
    description="Backend-часть сервиса для проведения игры Ночной Дозор.",
    version="alpha-0.0.2",
    lifespan=lifespan
)
app.include_router(security.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Hello World, i'm backend!"}

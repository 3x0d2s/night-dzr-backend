from fastapi import FastAPI
from app.security import security
from app.routers.users import users

app = FastAPI(
    title="NightDozor_Backend",
    description="Backend-часть сервиса для проведения игры Ночной Дозор.",
    version="alpha-0.0.1"
)
app.include_router(security.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Hello World, i'm backend!"}

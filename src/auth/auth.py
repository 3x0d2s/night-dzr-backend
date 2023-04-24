from fastapi_users.authentication import BearerTransport
from fastapi_users.authentication import JWTStrategy
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users import FastAPIUsers
from config.config_reader import config
from src.auth.manager import get_user_manager
from src.models.user import User


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=config.SECURITY_KEY.get_secret_value(),
                       lifetime_seconds=config.ACCESS_TOKEN_EXPIRE_SECONDS)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="auth/jwt/login"),
    get_strategy=get_jwt_strategy,
)
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
current_user = fastapi_users.current_user()

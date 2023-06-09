from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    SECURITY_KEY: SecretStr
    ACCESS_TOKEN_EXPIRE_SECONDS: int

    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB_NAME: str
    POSTGRES_DB_NAME_TEST: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()

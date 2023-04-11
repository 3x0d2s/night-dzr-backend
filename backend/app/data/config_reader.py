from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    SECURITY_KEY: SecretStr
    TOKEN_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB_NAME: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Config(BaseSettings):
    auth_key: str = "auth_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    database_url: str = Field(
        "postgresql://postgres:postgres@localhost/auth_db", alias="AUTH_DATABASE_URL"
    )

    model_config = SettingsConfigDict(env_file=".env")


config = Config()

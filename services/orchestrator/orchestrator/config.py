from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    model_config = SettingsConfigDict(env_file=".env")


config = Config()

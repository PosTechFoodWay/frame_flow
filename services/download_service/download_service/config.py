from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    auth_service_url: str = "http://host.internal.docker:8000"

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    aws_access_key_id: str = "TEST_ACCESS"
    aws_secret_access_key: str = "TEST_SECRET"
    aws_session_token: str = ""
    s3_bucket_name: str = "my-bucket"
    aws_region_name: str = "us-east-1"

    model_config = SettingsConfigDict(env_file=".env")


config = Config()

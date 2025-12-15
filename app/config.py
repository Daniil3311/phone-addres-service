from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


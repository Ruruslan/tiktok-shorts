from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'TikTok Shorts Studio'
    environment: str = 'development'
    api_prefix: str = '/api/v1'
    frontend_origin: str = 'http://localhost:5173'
    cors_origins: list[AnyHttpUrl] | list[str] = Field(default_factory=lambda: ['http://localhost:5173'])
    csrf_token: str = 'change-me-in-production'
    openai_api_key: str = ''
    openai_model: str = 'gpt-4.1-mini'
    whisper_model: str = 'gpt-4o-mini-transcribe'
    redis_url: str = 'redis://redis:6379/0'
    database_url: str = 'sqlite:///./app.db'
    temp_root: Path = Path('./tmp')
    public_root: Path = Path('./public')
    max_video_minutes: int = 90
    max_video_bytes: int = 1_500_000_000
    rate_limit: str = '10/minute'
    allowed_hosts: tuple[str, ...] = ('youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com')
    clip_target_count: int = 10
    clip_min_seconds: int = 15
    clip_max_seconds: int = 60

    @field_validator('temp_root', 'public_root', mode='before')
    @classmethod
    def _expand_path(cls, value: str | Path) -> Path:
        return Path(value).expanduser().resolve()


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.temp_root.mkdir(parents=True, exist_ok=True)
    settings.public_root.mkdir(parents=True, exist_ok=True)
    return settings

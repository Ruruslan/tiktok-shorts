from datetime import datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl

JobStatus = Literal['queued', 'processing', 'completed', 'failed']


class ClipAsset(BaseModel):
    clip_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    summary: str
    start_seconds: float
    end_seconds: float
    duration_seconds: float
    transcript_excerpt: str
    file_path: str | None = None
    subtitles_path: str | None = None


class JobRecord(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    source_url: HttpUrl
    status: JobStatus = 'queued'
    progress: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error: str | None = None
    clips: list[ClipAsset] = Field(default_factory=list)
    task_id: str | None = None

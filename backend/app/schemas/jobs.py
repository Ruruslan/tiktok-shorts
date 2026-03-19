from pydantic import BaseModel, HttpUrl

from app.models.job import ClipAsset, JobStatus


class CreateJobRequest(BaseModel):
    youtube_url: HttpUrl


class RegenerateClipRequest(BaseModel):
    clip_id: str


class ClipResponse(ClipAsset):
    pass


class JobResponse(BaseModel):
    job_id: str
    source_url: HttpUrl
    status: JobStatus
    progress: int
    error: str | None
    clips: list[ClipResponse]

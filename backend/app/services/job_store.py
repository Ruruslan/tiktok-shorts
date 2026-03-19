import json
from datetime import datetime
from threading import Lock
from typing import Any

from app.core.config import get_settings
from app.models.job import ClipAsset, JobRecord


class FileJobStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._root = get_settings().temp_root / 'jobs'
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, job_id: str):
        return self._root / f'{job_id}.json'

    def _write(self, job: JobRecord) -> None:
        self._path(job.job_id).write_text(job.model_dump_json(indent=2), encoding='utf-8')

    def _load(self, job_id: str) -> JobRecord | None:
        path = self._path(job_id)
        if not path.exists():
            return None
        return JobRecord.model_validate(json.loads(path.read_text(encoding='utf-8')))

    def create(self, job: JobRecord) -> JobRecord:
        with self._lock:
            self._write(job)
        return job

    def get(self, job_id: str) -> JobRecord | None:
        return self._load(job_id)

    def update(self, job_id: str, **fields: Any) -> JobRecord:
        with self._lock:
            job = self._load(job_id)
            if not job:
                raise KeyError(job_id)
            for key, value in fields.items():
                setattr(job, key, value)
            job.updated_at = datetime.utcnow()
            self._write(job)
            return job

    def replace_clip(self, job_id: str, clip_id: str, new_clip: ClipAsset) -> JobRecord:
        with self._lock:
            job = self._load(job_id)
            if not job:
                raise KeyError(job_id)
            job.clips = [new_clip if clip.clip_id == clip_id else clip for clip in job.clips]
            job.updated_at = datetime.utcnow()
            self._write(job)
            return job


job_store = FileJobStore()

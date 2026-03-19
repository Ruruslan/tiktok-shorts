from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import validate_youtube_url, verify_csrf
from app.models.job import JobRecord
from app.schemas.jobs import CreateJobRequest, JobResponse, RegenerateClipRequest
from app.services.job_store import job_store
from app.services.youtube import youtube_service
from app.workers.tasks import process_job, regenerate_clip

router = APIRouter(prefix='/jobs', tags=['jobs'])


@router.post('', response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(verify_csrf)])
def create_job(payload: CreateJobRequest) -> JobResponse:
    url = validate_youtube_url(str(payload.youtube_url))
    youtube_service.probe(url)
    job = job_store.create(JobRecord(source_url=url))
    task = process_job.delay(job.job_id)
    job_store.update(job.job_id, task_id=task.id)
    return JobResponse(**job.model_dump())


@router.get('/{job_id}', response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found.')
    return JobResponse(**job.model_dump())


@router.post('/{job_id}/regenerate', response_model=JobResponse, dependencies=[Depends(verify_csrf)])
def regenerate(job_id: str, payload: RegenerateClipRequest) -> JobResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Job not found.')
    regenerate_clip.delay(job_id, payload.clip_id)
    return JobResponse(**job.model_dump())

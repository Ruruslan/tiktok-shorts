from pathlib import Path
from uuid import uuid4

from app.models.job import ClipAsset
from app.services.job_store import job_store
from app.services.segmentation import segmentation_service
from app.services.transcription import transcription_service
from app.services.video import video_service
from app.services.youtube import youtube_service
from app.workers.celery_app import celery_app
from app.core.config import get_settings


@celery_app.task(name='process_job')
def process_job(job_id: str) -> None:
    settings = get_settings()
    job = job_store.get(job_id)
    if not job:
        return
    work_dir = settings.temp_root / job_id
    clip_dir = settings.public_root / job_id
    work_dir.mkdir(parents=True, exist_ok=True)
    clip_dir.mkdir(parents=True, exist_ok=True)
    try:
        job_store.update(job_id, status='processing', progress=5)
        source_video = youtube_service.download(str(job.source_url), work_dir)
        job_store.update(job_id, progress=25)
        transcript = transcription_service.transcribe(source_video, work_dir)
        job_store.update(job_id, progress=50)
        clip_specs = segmentation_service.propose_clips(transcript)
        clips: list[ClipAsset] = []
        for index, spec in enumerate(clip_specs, start=1):
            if spec['end_seconds'] - spec['start_seconds'] < settings.clip_min_seconds:
                spec['end_seconds'] = min(spec['start_seconds'] + settings.clip_min_seconds, spec['start_seconds'] + settings.clip_max_seconds)
            clip_path, subtitle_path = video_service.render_clip(source_video, clip_dir, spec)
            clips.append(ClipAsset(
                title=spec['title'],
                summary=spec['summary'],
                start_seconds=spec['start_seconds'],
                end_seconds=spec['end_seconds'],
                duration_seconds=spec['end_seconds'] - spec['start_seconds'],
                transcript_excerpt=spec['transcript_excerpt'],
                file_path=f'/public/{job_id}/{clip_path.name}',
                subtitles_path=f'/public/{job_id}/{subtitle_path.name}',
            ))
            job_store.update(job_id, progress=min(95, 50 + index * 4))
        job_store.update(job_id, status='completed', progress=100, clips=clips)
    except Exception as exc:  # noqa: BLE001
        job_store.update(job_id, status='failed', error=str(exc), progress=100)


@celery_app.task(name='regenerate_clip')
def regenerate_clip(job_id: str, clip_id: str) -> None:
    settings = get_settings()
    job = job_store.get(job_id)
    if not job:
        return
    work_dir = settings.temp_root / job_id
    clip_dir = settings.public_root / job_id
    work_dir.mkdir(parents=True, exist_ok=True)
    clip_dir.mkdir(parents=True, exist_ok=True)
    source_video = next(work_dir.glob('source.*'))
    transcript = __import__('json').loads((work_dir / 'transcript.json').read_text(encoding='utf-8'))
    specs = segmentation_service.propose_clips(transcript, regenerate_clip_id=clip_id, existing_excerpts=[c.transcript_excerpt for c in job.clips])
    replacement = next((spec for spec in specs if spec['transcript_excerpt'] not in {c.transcript_excerpt for c in job.clips}), specs[0])
    clip_path, subtitle_path = video_service.render_clip(source_video, clip_dir, replacement)
    new_clip = ClipAsset(
        clip_id=clip_id or str(uuid4()),
        title=replacement['title'],
        summary=replacement['summary'],
        start_seconds=replacement['start_seconds'],
        end_seconds=replacement['end_seconds'],
        duration_seconds=replacement['end_seconds'] - replacement['start_seconds'],
        transcript_excerpt=replacement['transcript_excerpt'],
        file_path=f'/public/{job_id}/{clip_path.name}',
        subtitles_path=f'/public/{job_id}/{subtitle_path.name}',
    )
    job_store.replace_clip(job_id, clip_id, new_clip)

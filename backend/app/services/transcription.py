import json
from pathlib import Path

from openai import OpenAI

from app.core.config import get_settings


class TranscriptionService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key) if self.settings.openai_api_key else None

    def transcribe(self, video_path: Path, output_dir: Path) -> dict:
        if not self.client:
            raise RuntimeError('OPENAI_API_KEY is required for transcription.')
        output_dir.mkdir(parents=True, exist_ok=True)
        with video_path.open('rb') as media_file:
            transcription = self.client.audio.transcriptions.create(
                model=self.settings.whisper_model,
                file=media_file,
                response_format='verbose_json',
                timestamp_granularities=['segment'],
            )
        payload = json.loads(transcription.model_dump_json())
        transcript_path = output_dir / 'transcript.json'
        transcript_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        return payload


transcription_service = TranscriptionService()

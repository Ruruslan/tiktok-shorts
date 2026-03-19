import json
import subprocess
from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.security import validate_youtube_url


class YouTubeService:
    def probe(self, url: str) -> dict:
        validate_youtube_url(url)
        cmd = [
            'yt-dlp',
            '--dump-single-json',
            '--no-warnings',
            '--no-playlist',
            url,
        ]
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            data = json.loads(result.stdout)
        except subprocess.CalledProcessError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unable to fetch YouTube metadata.') from exc

        duration = int(data.get('duration') or 0)
        if duration > get_settings().max_video_minutes * 60:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail='Video is too long.')
        return data

    def download(self, url: str, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_template = str(output_dir / 'source.%(ext)s')
        cmd = [
            'yt-dlp',
            '--no-playlist',
            '--max-filesize',
            str(get_settings().max_video_bytes),
            '-o',
            output_template,
            url,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unable to download source video.') from exc

        matches = list(output_dir.glob('source.*'))
        if not matches:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Download completed but file was not found.')
        return matches[0]


youtube_service = YouTubeService()

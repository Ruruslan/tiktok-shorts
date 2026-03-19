import json
import shutil
import subprocess
from pathlib import Path

import cv2

from app.core.config import get_settings


class VideoService:
    def extract_audio(self, video_path: Path, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = output_dir / 'audio.wav'
        cmd = ['ffmpeg', '-y', '-i', str(video_path), '-vn', '-ac', '1', '-ar', '16000', str(audio_path)]
        subprocess.run(cmd, check=True, capture_output=True)
        return audio_path

    def detect_focus_x(self, video_path: Path) -> float:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        classifier = cv2.CascadeClassifier(cascade_path)
        capture = cv2.VideoCapture(str(video_path))
        try:
            for _ in range(15):
                ok, frame = capture.read()
                if not ok:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = classifier.detectMultiScale(gray, 1.1, 4)
                if len(faces):
                    x, _, w, _ = faces[0]
                    return float(x + w / 2) / float(frame.shape[1])
        finally:
            capture.release()
        return 0.5

    def build_subtitles(self, transcript_excerpt: str, clip_path: Path, output_dir: Path) -> Path:
        subtitle_path = output_dir / f'{clip_path.stem}.srt'
        subtitle_path.write_text(
            '1\n00:00:00,000 --> 00:00:05,000\n' + transcript_excerpt.strip() + '\n',
            encoding='utf-8',
        )
        return subtitle_path

    def render_clip(self, source_video: Path, output_dir: Path, clip: dict) -> tuple[Path, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        probe = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', str(source_video)],
            check=True,
            capture_output=True,
            text=True,
        )
        stream = json.loads(probe.stdout)['streams'][0]
        width, height = int(stream['width']), int(stream['height'])
        focus_x = self.detect_focus_x(source_video)
        crop_width = max(int(height * 9 / 16), 1)
        max_x = max(width - crop_width, 0)
        crop_x = int(max(0, min(max_x, width * focus_x - crop_width / 2)))
        clip_path = output_dir / f"{clip.get('title', 'clip').replace(' ', '_').lower()}.mp4"
        subtitle_path = self.build_subtitles(clip['transcript_excerpt'], clip_path, output_dir)
        vf = (
            f"crop={crop_width}:{height}:{crop_x}:0,scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,subtitles='{subtitle_path.as_posix()}':force_style='Fontsize=18,PrimaryColour=&H00FFFFFF&,OutlineColour=&H000000&,BorderStyle=3,Outline=2,Alignment=2'"
        )
        cmd = [
            'ffmpeg', '-y', '-ss', str(clip['start_seconds']), '-to', str(clip['end_seconds']), '-i', str(source_video),
            '-vf', vf, '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-c:a', 'aac', '-movflags', '+faststart', str(clip_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return clip_path, subtitle_path

    def cleanup_job_dir(self, job_dir: Path) -> None:
        if job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)


video_service = VideoService()

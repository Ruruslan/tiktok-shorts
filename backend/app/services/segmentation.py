import json
import math
from dataclasses import dataclass

from openai import OpenAI

from app.core.config import get_settings


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


class SegmentationService:
    FILLERS = {'uh', 'um', 'you know', 'like', 'sort of', 'kind of'}

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key) if self.settings.openai_api_key else None

    def _normalize_segments(self, transcript: dict) -> list[TranscriptSegment]:
        segments: list[TranscriptSegment] = []
        for item in transcript.get('segments', []):
            text = ' '.join(word for word in item.get('text', '').split() if word.lower() not in self.FILLERS).strip()
            if not text:
                continue
            segments.append(TranscriptSegment(start=float(item['start']), end=float(item['end']), text=text))
        return segments

    def _fallback_plan(self, segments: list[TranscriptSegment]) -> list[dict]:
        total = len(segments)
        step = max(1, math.floor(total / self.settings.clip_target_count))
        clips: list[dict] = []
        for index in range(self.settings.clip_target_count):
            window = segments[index * step:(index + 1) * step + 1] or segments[-2:]
            start = max(window[0].start, 0)
            end = min(window[-1].end, start + self.settings.clip_max_seconds)
            if end - start < self.settings.clip_min_seconds and index + 1 < total:
                end = min(segments[min(total - 1, index * step + step)].end, start + self.settings.clip_max_seconds)
            clips.append({
                'title': f'Clip {index + 1}',
                'summary': window[0].text[:140],
                'start_seconds': start,
                'end_seconds': end,
                'transcript_excerpt': ' '.join(seg.text for seg in window)[:240],
            })
        return clips[: self.settings.clip_target_count]

    def propose_clips(self, transcript: dict, regenerate_clip_id: str | None = None, existing_excerpts: list[str] | None = None) -> list[dict]:
        segments = self._normalize_segments(transcript)
        if not self.client:
            return self._fallback_plan(segments)
        transcript_text = '\n'.join(f"[{seg.start:.2f}-{seg.end:.2f}] {seg.text}" for seg in segments)
        existing = existing_excerpts or []
        prompt = {
            'instruction': 'Return exactly 10 semantically complete vertical short clip suggestions from the transcript. Avoid clips starting or ending mid-sentence, avoid silence, avoid duplicates, prioritize emotional or insightful moments, keep each between 15 and 60 seconds.',
            'regenerate_clip_id': regenerate_clip_id,
            'avoid_excerpts': existing,
            'output_schema': {
                'clips': [
                    {
                        'title': 'string',
                        'summary': 'string',
                        'start_seconds': 0,
                        'end_seconds': 30,
                        'transcript_excerpt': 'string',
                    }
                ]
            },
        }
        response = self.client.chat.completions.create(
            model=self.settings.openai_model,
            response_format={'type': 'json_object'},
            messages=[
                {'role': 'system', 'content': 'You are an expert short-form video editor.'},
                {'role': 'user', 'content': json.dumps(prompt, ensure_ascii=False) + '\n\nTRANSCRIPT\n' + transcript_text},
            ],
        )
        content = response.choices[0].message.content or '{}'
        parsed = json.loads(content)
        clips = parsed.get('clips') or []
        if len(clips) < self.settings.clip_target_count:
            fallback = self._fallback_plan(segments)
            seen = {clip.get('transcript_excerpt') for clip in clips}
            for candidate in fallback:
                if candidate.get('transcript_excerpt') in seen:
                    continue
                clips.append(candidate)
                if len(clips) == self.settings.clip_target_count:
                    break
        return clips[: self.settings.clip_target_count] if clips else self._fallback_plan(segments)


segmentation_service = SegmentationService()

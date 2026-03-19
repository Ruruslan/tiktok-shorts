from app.services.segmentation import segmentation_service


def test_fallback_plan_returns_ten_clips() -> None:
    transcript = {
        'segments': [
            {'start': float(index * 10), 'end': float(index * 10 + 9), 'text': f'Segment {index} with a complete idea.'}
            for index in range(12)
        ]
    }
    clips = segmentation_service.propose_clips(transcript)
    assert len(clips) == 10
    assert all(clip['end_seconds'] > clip['start_seconds'] for clip in clips)

import pytest
from fastapi import HTTPException

from app.core.security import validate_youtube_url


def test_validate_youtube_url_accepts_known_hosts() -> None:
    assert validate_youtube_url('https://www.youtube.com/watch?v=abc123')


@pytest.mark.parametrize('url', ['http://youtube.com/watch?v=1', 'https://evil.com/video'])
def test_validate_youtube_url_rejects_invalid_hosts(url: str) -> None:
    with pytest.raises(HTTPException):
        validate_youtube_url(url)

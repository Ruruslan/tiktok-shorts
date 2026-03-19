from urllib.parse import urlparse

from fastapi import Header, HTTPException, Request, status

from app.core.config import get_settings


def validate_youtube_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {'https'}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Only HTTPS YouTube URLs are allowed.')
    settings = get_settings()
    host = parsed.netloc.lower()
    if host not in settings.allowed_hosts:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Unsupported YouTube host.')
    return url


async def verify_csrf(request: Request, x_csrf_token: str | None = Header(default=None)) -> None:
    if request.method in {'GET', 'HEAD', 'OPTIONS'}:
        return
    expected = get_settings().csrf_token
    if not expected or x_csrf_token != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid CSRF token.')

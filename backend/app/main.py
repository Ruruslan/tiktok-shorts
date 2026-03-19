from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1.jobs import router as jobs_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging()
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])
app = FastAPI(title=settings.app_name, default_response_class=ORJSONResponse)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_methods=['GET', 'POST', 'OPTIONS'],
    allow_headers=['Content-Type', 'X-CSRF-Token'],
    allow_credentials=False,
)
app.include_router(jobs_router, prefix=settings.api_prefix)
app.mount('/public', StaticFiles(directory=Path(settings.public_root)), name='public')


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}

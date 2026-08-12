from __future__ import annotations

import logging
from pathlib import Path
from typing import cast

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.types import ExceptionHandler

from app.api.routes import router
from app.core.config import settings
from app.core.rate_limit import limiter
from app.middleware.request_id import RequestIDMiddleware

logging.basicConfig(
    level=logging.INFO,
    format=("%(asctime)s %(levelname)s %(name)s %(message)s"),
)


BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


app.state.limiter = limiter


app.add_exception_handler(
    RateLimitExceeded,
    cast(
        ExceptionHandler,
        _rate_limit_exceeded_handler,
    ),
)


app.add_middleware(RequestIDMiddleware)


app.include_router(router)


app.mount(
    "/static",
    StaticFiles(
        directory=STATIC_DIR,
    ),
    name="static",
)


@app.get("/")
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")

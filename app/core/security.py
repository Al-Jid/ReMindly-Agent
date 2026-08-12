from __future__ import annotations

import secrets

from fastapi import (
    Header,
    HTTPException,
)

from app.core.config import (
    settings,
)


def verify_api_key(
    x_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
    ),
) -> None:
    configured_key = settings.APP_API_KEY

    # Local mode:
    # If no app key is configured,
    # API protection is disabled.
    if not configured_key:
        return

    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized.",
        )

    if not secrets.compare_digest(
        x_api_key,
        configured_key,
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized.",
        )

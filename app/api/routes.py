from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import (
    AsyncGenerator,
    Iterator,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from fastapi.responses import (
    StreamingResponse,
)

from app.core.config import settings
from app.core.prompts import (
    build_organizer_prompt,
)
from app.core.rate_limit import limiter
from app.core.security import (
    verify_api_key,
)
from app.models.schemas import (
    OrganizeRequest,
)
from app.services.chunker import (
    chunk_text,
    get_chunk_size_for_mode,
)
from app.services.llm import (
    clean_model_output,
    llm_service,
)
from app.services.organizer import (
    Candidate,
    organizer_service,
)
from app.services.reviewer import (
    reviewer_service,
)
from app.services.validator import (
    MarkdownValidationResult,
    validate_markdown,
)

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api",
    tags=["notes"],
)


def sse_event(
    event: str,
    data: dict,
    event_id: str | None = None,
) -> str:
    payload = json.dumps(
        data,
        ensure_ascii=False,
    )

    lines: list[str] = []

    if event_id:
        lines.append(f"id: {event_id}")

    lines.append(f"event: {event}")
    lines.append(f"data: {payload}")

    return "\n".join(lines) + "\n\n"


def request_id_from(
    request: Request,
) -> str:
    return getattr(
        request.state,
        "request_id",
        "unknown",
    )


def serialize_validation(
    validation: MarkdownValidationResult,
) -> dict[str, object]:
    return {
        "valid": validation.valid,
        "issues": [
            {
                "code": issue.code,
                "message": issue.message,
                "severity": issue.severity,
            }
            for issue in validation.issues
        ],
    }


def _next_stream_item(
    iterator: Iterator[str],
) -> tuple[
    bool,
    str | None,
]:
    try:
        return (
            False,
            next(iterator),
        )

    except StopIteration:
        return (
            True,
            None,
        )


@router.get("/health")
def health() -> dict[str, object]:
    checks = llm_service.configuration_status()

    checks.update(
        {
            "chunk_size_valid": settings.CHUNK_SIZE > 0,
            "fast_chunk_size_valid": settings.FAST_CHUNK_SIZE > 0,
            "max_chunks_valid": settings.MAX_CHUNKS > 0,
            "output_budget_valid": settings.MAX_OUTPUT_TOKENS > 0,
            "parallelism_valid": settings.MAX_PARALLEL_CHUNKS > 0,
        }
    )

    healthy = all(checks.values())

    return {
        "status": "ok" if healthy else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "checks": checks,
    }


@router.post("/organize")
@limiter.limit(settings.ORGANIZE_RATE_LIMIT)
def organize(
    request: Request,
    payload: OrganizeRequest,
    _: None = Depends(verify_api_key),
) -> dict[str, object]:
    request_id = request_id_from(request)

    try:
        result = organizer_service.organize(
            text=payload.text,
            instruction=payload.instruction,
            mode=payload.mode,
            language=payload.language,
            detail_level=payload.detail_level,
        )

        return {
            "markdown": result.markdown,
            "mode": payload.mode,
            "language": payload.language,
            "detail_level": payload.detail_level,
            "reviewed": result.reviewed,
            "retried": result.retried,
            "processing_time": result.processing_time,
            "input_characters": result.input_characters,
            "output_characters": result.output_characters,
            "request_id": request_id,
            "validation": serialize_validation(result.validation),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Failed to organize notes request_id=%s",
            request_id,
        )

        raise HTTPException(
            status_code=500,
            detail={
                "message": "An internal error occurred.",
                "request_id": request_id,
            },
        ) from exc


@router.post("/organize/stream")
@limiter.limit(settings.STREAM_RATE_LIMIT)
async def organize_stream(
    request: Request,
    payload: OrganizeRequest,
    _: None = Depends(verify_api_key),
) -> StreamingResponse:
    request_id = request_id_from(request)

    async def client_disconnected() -> bool:
        try:
            return await request.is_disconnected()

        except Exception:
            return False

    async def event_generator() -> AsyncGenerator[
        str,
        None,
    ]:
        started_at = time.perf_counter()

        source = payload.text.strip()

        if not source:
            yield sse_event(
                "error",
                {
                    "message": "Input text cannot be empty.",
                    "request_id": request_id,
                },
            )

            return

        try:
            yield sse_event(
                "progress",
                {
                    "stage": "input_received",
                    "label": "Input received",
                    "progress": 10,
                    "input_characters": len(source),
                },
            )

            system_prompt = build_organizer_prompt(
                language=payload.language,
                detail_level=payload.detail_level,
                mode=payload.mode,
                extra_instruction=payload.instruction,
            )

            yield sse_event(
                "progress",
                {
                    "stage": "preparing",
                    "label": "Preparing instructions",
                    "progress": 20,
                },
            )

            single_pass = organizer_service.should_use_single_pass(
                source,
                payload.mode,
            )

            # ==================================================
            # SINGLE PASS
            # ==================================================

            if single_pass:
                yield sse_event(
                    "progress",
                    {
                        "stage": "generating",
                        "label": "Generating Markdown",
                        "progress": 30,
                    },
                )

                user_prompt = organizer_service.build_user_prompt(text=source)

                iterator = iter(
                    llm_service.stream(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        max_tokens=(
                            organizer_service.output_budget(
                                payload.detail_level,
                                payload.mode,
                            )
                        ),
                    )
                )

                parts: list[str] = []
                generated_characters = 0

                while True:
                    if await client_disconnected():
                        return

                    (
                        finished,
                        text_chunk,
                    ) = await asyncio.to_thread(
                        _next_stream_item,
                        iterator,
                    )

                    if finished:
                        break

                    if not text_chunk:
                        continue

                    parts.append(text_chunk)

                    generated_characters += len(text_chunk)

                    yield sse_event(
                        "token",
                        {
                            "text": text_chunk,
                            "output_characters": (generated_characters),
                        },
                    )

                markdown = clean_model_output("".join(parts))

                # Replace streamed content if cleaning
                # removed meta reasoning.
                if markdown != "".join(parts).strip():
                    yield sse_event(
                        "replace",
                        {
                            "markdown": markdown,
                        },
                    )

            # ==================================================
            # MULTI CHUNK
            # ==================================================

            else:
                chunk_size = get_chunk_size_for_mode(payload.mode)

                source_chunks = chunk_text(
                    source,
                    chunk_size=chunk_size,
                )

                total_chunks = len(source_chunks)

                yield sse_event(
                    "progress",
                    {
                        "stage": "generating",
                        "label": (f"Processing {total_chunks} sections"),
                        "progress": 30,
                        "total_chunks": total_chunks,
                    },
                )

                # Chunk generation happens in parallel
                # inside OrganizerService.
                generated_chunks = await asyncio.to_thread(
                    organizer_service.generate_chunks_parallel,
                    source_chunks,
                    system_prompt,
                    payload.detail_level,
                    payload.mode,
                )

                if await client_disconnected():
                    return

                yield sse_event(
                    "progress",
                    {
                        "stage": "generating",
                        "label": (
                            "Combining sections"
                            if payload.mode == "fast"
                            else "Merging sections"
                        ),
                        "progress": 75,
                    },
                )

                markdown = await asyncio.to_thread(
                    organizer_service.merge_chunks,
                    generated_chunks,
                    system_prompt,
                    payload.detail_level,
                    payload.mode,
                )

                markdown = clean_model_output(markdown)

                yield sse_event(
                    "replace",
                    {
                        "markdown": markdown,
                    },
                )

            # ==================================================
            # VALIDATION
            # ==================================================

            yield sse_event(
                "progress",
                {
                    "stage": "validating",
                    "label": "Validating Markdown",
                    "progress": 85,
                },
            )

            validation = validate_markdown(
                markdown=markdown,
                source_text=source,
                expected_language=payload.language,
                detail_level=payload.detail_level,
            )

            candidates = [
                Candidate(
                    markdown=markdown,
                    validation=validation,
                )
            ]

            # ==================================================
            # FAST
            # ==================================================

            if payload.mode == "fast":
                best = candidates[0]

            # ==================================================
            # BALANCED / QUALITY REVIEW
            # ==================================================

            else:
                should_review = payload.mode == "quality" or (
                    payload.mode == "balanced" and not validation.valid
                )

                if should_review:
                    yield sse_event(
                        "progress",
                        {
                            "stage": "reviewing",
                            "label": "Reviewing quality",
                            "progress": 91,
                        },
                    )

                    reviewed = await asyncio.to_thread(
                        reviewer_service.review,
                        source,
                        markdown,
                        payload.language,
                        payload.detail_level,
                    )

                    reviewed = clean_model_output(reviewed)

                    reviewed_validation = validate_markdown(
                        markdown=reviewed,
                        source_text=source,
                        expected_language=(payload.language),
                    )

                    candidates.append(
                        Candidate(
                            markdown=reviewed,
                            validation=(reviewed_validation),
                            reviewed=True,
                        )
                    )

                    # Retry is only worth the
                    # extra latency in Quality mode.
                    if (
                        payload.mode == "quality"
                        and not reviewed_validation.valid
                        and (settings.MAX_GENERATION_RETRIES > 0)
                    ):
                        errors = [
                            (f"{issue.code}: {issue.message}")
                            for issue in (reviewed_validation.issues)
                            if issue.severity == "error"
                        ]

                        yield sse_event(
                            "progress",
                            {
                                "stage": "reviewing",
                                "label": ("Repairing validation problems"),
                                "progress": 95,
                            },
                        )

                        repaired = await asyncio.to_thread(
                            reviewer_service.repair,
                            source,
                            reviewed,
                            errors,
                            payload.language,
                            payload.detail_level,
                        )

                        repaired = clean_model_output(repaired)

                        repaired_validation = validate_markdown(
                            markdown=repaired,
                            source_text=source,
                            expected_language=(payload.language),
                        )

                        candidates.append(
                            Candidate(
                                markdown=repaired,
                                validation=(repaired_validation),
                                reviewed=True,
                                retried=True,
                            )
                        )

                best = organizer_service.choose_best_candidate(candidates)

            final_markdown = best.markdown.strip()

            if final_markdown != markdown:
                yield sse_event(
                    "replace",
                    {
                        "markdown": final_markdown,
                    },
                )

            yield sse_event(
                "progress",
                {
                    "stage": "finalizing",
                    "label": "Finalizing",
                    "progress": 98,
                },
            )

            elapsed = round(
                time.perf_counter() - started_at,
                3,
            )

            yield sse_event(
                "completed",
                {
                    "markdown": final_markdown,
                    "reviewed": best.reviewed,
                    "retried": best.retried,
                    "processing_time": elapsed,
                    "input_characters": len(source),
                    "output_characters": len(final_markdown),
                    "request_id": request_id,
                    "validation": (serialize_validation(best.validation)),
                },
            )

        except ValueError as exc:
            logger.warning(
                ("Invalid streaming request request_id=%s error=%s"),
                request_id,
                exc,
            )

            yield sse_event(
                "error",
                {
                    "message": str(exc),
                    "request_id": request_id,
                },
            )

        except Exception:
            logger.exception(
                ("Streaming organization failed request_id=%s"),
                request_id,
            )

            yield sse_event(
                "error",
                {
                    "message": ("An internal error occurred."),
                    "request_id": request_id,
                },
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

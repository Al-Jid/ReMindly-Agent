from __future__ import annotations

import json
import time
from collections.abc import Generator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import OrganizeRequest
from app.services.organizer import organizer_service
from app.services.llm import llm_service
from app.core.prompts import build_organizer_prompt
from app.services.validator import validate_markdown
from app.services.reviewer import reviewer_service


router = APIRouter(prefix="/api", tags=["notes"])


def sse_event(
    event: str,
    data: dict,
) -> str:
    payload = json.dumps(
        data,
        ensure_ascii=False,
    )

    return f"event: {event}\ndata: {payload}\n\n"


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "MD Notes Agent",
    }


@router.post("/organize")
def organize(payload: OrganizeRequest):
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
            "processing_time": result.processing_time,
            "input_characters": result.input_characters,
            "output_characters": result.output_characters,
            "validation": {
                "valid": result.validation.valid,
                "issues": [
                    {
                        "code": issue.code,
                        "message": issue.message,
                        "severity": issue.severity,
                    }
                    for issue in result.validation.issues
                ],
            },
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.post("/organize/stream")
def organize_stream(
    payload: OrganizeRequest,
):
    def event_generator() -> Generator[str, None, None]:
        started_at = time.perf_counter()

        source = payload.text.strip()

        if not source:
            yield sse_event(
                "error",
                {
                    "message": "Input text cannot be empty.",
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

            yield sse_event(
                "progress",
                {
                    "stage": "preparing",
                    "label": "Preparing instructions",
                    "progress": 20,
                },
            )

            system_prompt = build_organizer_prompt(
                language=payload.language,
                detail_level=payload.detail_level,
                mode=payload.mode,
                extra_instruction=payload.instruction,
            )

            user_prompt = f"""
Organize the following source into clean Markdown notes.

SOURCE:

{source}
""".strip()

            yield sse_event(
                "progress",
                {
                    "stage": "generating",
                    "label": "Generating Markdown",
                    "progress": 30,
                },
            )

            chunks: list[str] = []
            generated_characters = 0

            for text_chunk in llm_service.stream(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            ):
                chunks.append(text_chunk)
                generated_characters += len(text_chunk)

                yield sse_event(
                    "token",
                    {
                        "text": text_chunk,
                        "output_characters": generated_characters,
                    },
                )

            markdown = "".join(chunks).strip()

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
            )

            reviewed = False

            should_review = False

            if payload.mode == "quality":
                should_review = True

            elif payload.mode == "balanced":
                should_review = not validation.valid or any(
                    issue.severity
                    in {
                        "warning",
                        "error",
                    }
                    for issue in validation.issues
                )

            if should_review:
                yield sse_event(
                    "progress",
                    {
                        "stage": "reviewing",
                        "label": "Reviewing quality",
                        "progress": 90,
                    },
                )

                markdown = reviewer_service.review(
                    source_text=source,
                    generated_markdown=markdown,
                )

                reviewed = True

                validation = validate_markdown(
                    markdown=markdown,
                    source_text=source,
                    expected_language=payload.language,
                )

                yield sse_event(
                    "replace",
                    {
                        "markdown": markdown,
                    },
                )

            yield sse_event(
                "progress",
                {
                    "stage": "finalizing",
                    "label": "Finalizing",
                    "progress": 97,
                },
            )

            elapsed = round(
                time.perf_counter() - started_at,
                3,
            )

            yield sse_event(
                "completed",
                {
                    "markdown": markdown,
                    "reviewed": reviewed,
                    "processing_time": elapsed,
                    "input_characters": len(source),
                    "output_characters": len(markdown),
                    "validation": {
                        "valid": validation.valid,
                        "issues": [
                            {
                                "code": issue.code,
                                "message": issue.message,
                                "severity": issue.severity,
                            }
                            for issue in validation.issues
                        ],
                    },
                },
            )

        except Exception as exc:
            yield sse_event(
                "error",
                {
                    "message": str(exc),
                },
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

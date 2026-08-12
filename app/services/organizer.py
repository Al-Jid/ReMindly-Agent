from __future__ import annotations

import time
from dataclasses import dataclass

from app.core.prompts import build_organizer_prompt
from app.services.chunker import chunk_text, should_chunk
from app.services.llm import llm_service
from app.services.reviewer import reviewer_service
from app.services.validator import (
    MarkdownValidationResult,
    validate_markdown,
)


@dataclass
class OrganizationResult:
    markdown: str

    reviewed: bool

    processing_time: float

    input_characters: int

    output_characters: int

    validation: MarkdownValidationResult


class OrganizerService:
    def _build_user_prompt(
        self,
        text: str,
        chunk_index: int | None = None,
        total_chunks: int | None = None,
    ) -> str:
        if chunk_index is not None and total_chunks is not None:
            return f"""
This is chunk {chunk_index} of {total_chunks}.

Organize ONLY this chunk.

Do not invent content from other chunks.

SOURCE:

{text}
""".strip()

        return f"""
Organize the following source into clean Markdown notes.

SOURCE:

{text}
""".strip()

    def _organize_single(
        self,
        text: str,
        system_prompt: str,
    ) -> str:
        user_prompt = self._build_user_prompt(
            text=text,
        )

        return llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def _organize_chunks(
        self,
        text: str,
        system_prompt: str,
    ) -> str:
        chunks = chunk_text(text)

        generated_chunks: list[str] = []

        total = len(chunks)

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):
            user_prompt = self._build_user_prompt(
                text=chunk,
                chunk_index=index,
                total_chunks=total,
            )

            result = llm_service.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

            generated_chunks.append(result.strip())

        return "\n\n---\n\n".join(generated_chunks)

    def organize(
        self,
        text: str,
        language: str = "auto",
        detail_level: str = "preserve",
        mode: str = "balanced",
        instruction: str | None = None,
    ) -> OrganizationResult:
        started_at = time.perf_counter()

        source = text.strip()

        if not source:
            raise ValueError("Input text cannot be empty.")

        system_prompt = build_organizer_prompt(
            language=language,
            detail_level=detail_level,
            mode=mode,
            extra_instruction=instruction,
        )

        if should_chunk(source):
            markdown = self._organize_chunks(
                text=source,
                system_prompt=system_prompt,
            )
        else:
            markdown = self._organize_single(
                text=source,
                system_prompt=system_prompt,
            )

        validation = validate_markdown(
            markdown=markdown,
            source_text=source,
            expected_language=language,
        )

        reviewed = False

        should_review = False

        if mode == "quality":
            should_review = True

        elif mode == "balanced":
            should_review = not validation.valid or any(
                issue.severity
                in {
                    "warning",
                    "error",
                }
                for issue in validation.issues
            )

        elif mode == "fast":
            should_review = False

        if should_review:
            markdown = reviewer_service.review(
                source_text=source,
                generated_markdown=markdown,
            )

            reviewed = True

            validation = validate_markdown(
                markdown=markdown,
                source_text=source,
                expected_language=language,
            )

        finished_at = time.perf_counter()

        return OrganizationResult(
            markdown=markdown.strip(),
            reviewed=reviewed,
            processing_time=round(
                finished_at - started_at,
                3,
            ),
            input_characters=len(source),
            output_characters=len(markdown),
            validation=validation,
        )


organizer_service = OrganizerService()

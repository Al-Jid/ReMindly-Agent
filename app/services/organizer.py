from __future__ import annotations

import re
import time
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from dataclasses import dataclass

from app.core.config import settings
from app.core.prompts import (
    build_organizer_prompt,
)
from app.services.chunker import (
    chunk_text,
    get_chunk_size_for_mode,
)
from app.services.llm import (
    clean_model_output,
    llm_service,
)
from app.services.reviewer import (
    reviewer_service,
)
from app.services.validator import (
    MarkdownValidationResult,
    validate_markdown,
    validation_score,
)


@dataclass
class OrganizationResult:
    markdown: str

    reviewed: bool

    retried: bool

    processing_time: float

    input_characters: int

    output_characters: int

    validation: MarkdownValidationResult


@dataclass
class Candidate:
    markdown: str

    validation: MarkdownValidationResult

    reviewed: bool = False

    retried: bool = False


class OrganizerService:
    def build_user_prompt(
        self,
        text: str,
        chunk_index: int | None = None,
        total_chunks: int | None = None,
    ) -> str:
        if chunk_index is not None and total_chunks is not None:
            return f"""
Organize ONLY this source segment into Markdown notes.

This is source segment {chunk_index} of {total_chunks}.

IMPORTANT:
- Return only Markdown.
- Do not discuss the segment number.
- Do not explain your reasoning.
- Do not say you are merging or processing chunks.
- Preserve the source meaning.
- Follow the requested detail level.
- Do not invent facts.

SOURCE:

{text}
""".strip()

        return f"""
Organize the following source into Markdown notes.

IMPORTANT:
- Return only the final Markdown.
- Do not explain your reasoning.
- Do not describe what you are doing.
- Follow the requested detail level exactly.
- Do not invent facts.

SOURCE:

{text}
""".strip()

    def output_budget(
        self,
        detail_level: str,
        mode: str,
    ) -> int:
        return settings.output_token_budget(
            detail_level,
            mode,
        )

    def chunk_budget(
        self,
        detail_level: str,
        mode: str,
    ) -> int:
        return settings.chunk_output_token_budget(
            detail_level,
            mode,
        )

    def should_use_single_pass(
        self,
        source: str,
        mode: str,
    ) -> bool:
        if mode == "fast":
            return len(source) <= settings.FAST_SINGLE_PASS_MAX_CHARS

        return len(source) <= settings.CHUNK_SIZE

    def _organize_single(
        self,
        text: str,
        system_prompt: str,
        detail_level: str,
        mode: str,
    ) -> str:
        user_prompt = self.build_user_prompt(
            text=text,
        )

        result = llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=(
                self.output_budget(
                    detail_level,
                    mode,
                )
            ),
        )

        return clean_model_output(result)

    def _generate_chunk(
        self,
        chunk: str,
        index: int,
        total: int,
        system_prompt: str,
        detail_level: str,
        mode: str,
    ) -> tuple[int, str]:
        prompt = self.build_user_prompt(
            text=chunk,
            chunk_index=index,
            total_chunks=total,
        )

        result = llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=prompt,
            max_tokens=(
                self.chunk_budget(
                    detail_level,
                    mode,
                )
            ),
        )

        return (
            index,
            clean_model_output(result),
        )

    def generate_chunks_parallel(
        self,
        chunks: list[str],
        system_prompt: str,
        detail_level: str,
        mode: str,
    ) -> list[str]:
        total = len(chunks)

        if total == 1:
            _, result = self._generate_chunk(
                chunk=chunks[0],
                index=1,
                total=1,
                system_prompt=(system_prompt),
                detail_level=(detail_level),
                mode=mode,
            )

            return [result]

        workers = min(
            settings.MAX_PARALLEL_CHUNKS,
            total,
        )

        results: dict[int, str] = {}

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(
                    self._generate_chunk,
                    chunk,
                    index,
                    total,
                    system_prompt,
                    detail_level,
                    mode,
                )
                for index, chunk in enumerate(
                    chunks,
                    start=1,
                )
            ]

            for future in as_completed(futures):
                index, result = future.result()

                if not result:
                    raise RuntimeError(f"Chunk {index} returned an empty result.")

                results[index] = result

        return [
            results[index]
            for index in range(
                1,
                total + 1,
            )
        ]

    def fast_merge_chunks(
        self,
        generated_chunks: list[str],
    ) -> str:
        cleaned: list[str] = []

        for index, chunk in enumerate(generated_chunks):
            chunk = clean_model_output(chunk).strip()

            if not chunk:
                continue

            if index > 0:
                # Remove an additional H1 title
                # from later chunks.
                chunk = re.sub(
                    r"\A\s*#\s+[^\n]+\n+",
                    "",
                    chunk,
                    count=1,
                ).strip()

            cleaned.append(chunk)

        if not cleaned:
            raise RuntimeError("No generated content is available.")

        return "\n\n".join(cleaned).strip()

    def merge_chunks(
        self,
        generated_chunks: list[str],
        system_prompt: str,
        detail_level: str = "preserve",
        mode: str = "balanced",
    ) -> str:
        cleaned_chunks = [
            clean_model_output(chunk).strip()
            for chunk in generated_chunks
            if chunk.strip()
        ]

        if not cleaned_chunks:
            raise ValueError("No generated chunks to merge.")

        if len(cleaned_chunks) == 1:
            return cleaned_chunks[0]

        if mode == "fast":
            return self.fast_merge_chunks(cleaned_chunks)

        combined = ("\n\n----- CHUNK BOUNDARY -----\n\n").join(cleaned_chunks)

        user_prompt = f"""
Return ONE final Markdown document by combining the
organized Markdown sections below.

CRITICAL:
- Output Markdown only.
- Do not output analysis or reasoning.
- Do not describe how you merged the sections.
- Never mention chunks or chunk boundaries.
- Remove exact duplication.
- Fix duplicate headings.
- Preserve logical order.
- Do not add external information.
- Follow the requested detail level.
- Do not expand the content unnecessarily.

MARKDOWN SECTIONS:

{combined}
""".strip()

        merged = llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=(
                self.output_budget(
                    detail_level,
                    mode,
                )
            ),
        )

        merged = clean_model_output(merged)

        if not merged:
            raise RuntimeError("Chunk merge returned an empty result.")

        return merged

    def organize_initial(
        self,
        source: str,
        system_prompt: str,
        detail_level: str,
        mode: str,
    ) -> str:
        if self.should_use_single_pass(
            source,
            mode,
        ):
            return self._organize_single(
                text=source,
                system_prompt=(system_prompt),
                detail_level=(detail_level),
                mode=mode,
            )

        chunk_size = get_chunk_size_for_mode(mode)

        chunks = chunk_text(
            source,
            chunk_size=chunk_size,
        )

        generated_chunks = self.generate_chunks_parallel(
            chunks=chunks,
            system_prompt=(system_prompt),
            detail_level=(detail_level),
            mode=mode,
        )

        return self.merge_chunks(
            generated_chunks=(generated_chunks),
            system_prompt=(system_prompt),
            detail_level=(detail_level),
            mode=mode,
        )

    def validate_candidate(
        self,
        markdown: str,
        source: str,
        language: str,
        detail_level: str,
    ) -> MarkdownValidationResult:
        return validate_markdown(
            markdown=markdown,
            source_text=source,
            expected_language=language,
            detail_level=detail_level,
        )

    def choose_best_candidate(
        self,
        candidates: list[Candidate],
    ) -> Candidate:
        if not candidates:
            raise RuntimeError("No generation candidate is available.")

        return max(
            candidates,
            key=lambda candidate: validation_score(candidate.validation),
        )

    def improve_candidate(
        self,
        source: str,
        markdown: str,
        language: str,
        detail_level: str,
        mode: str,
    ) -> Candidate:
        initial_validation = self.validate_candidate(
            markdown=markdown,
            source=source,
            language=language,
            detail_level=detail_level,
        )

        initial = Candidate(
            markdown=markdown,
            validation=initial_validation,
        )

        # FAST means FAST.
        # No second LLM call.
        if mode == "fast":
            return initial

        candidates = [initial]

        should_review = mode == "quality" or (
            mode == "balanced" and not (initial_validation.valid)
        )

        if not should_review:
            return initial

        reviewed_markdown = reviewer_service.review(
            source_text=source,
            generated_markdown=(markdown),
            expected_language=(language),
            detail_level=(detail_level),
        )

        reviewed_markdown = clean_model_output(reviewed_markdown)

        reviewed_validation = self.validate_candidate(
            markdown=(reviewed_markdown),
            source=source,
            language=language,
            detail_level=detail_level,
        )

        candidates.append(
            Candidate(
                markdown=(reviewed_markdown),
                validation=(reviewed_validation),
                reviewed=True,
            )
        )

        retry_count = 0

        current_markdown = reviewed_markdown

        current_validation = reviewed_validation

        while (
            mode == "quality"
            and not current_validation.valid
            and retry_count < settings.MAX_GENERATION_RETRIES
        ):
            validation_messages = [
                (f"{issue.code}: {issue.message}")
                for issue in current_validation.issues
                if (issue.severity == "error")
            ]

            repaired = reviewer_service.repair(
                source_text=source,
                generated_markdown=(current_markdown),
                validation_messages=(validation_messages),
                expected_language=(language),
                detail_level=(detail_level),
            )

            repaired = clean_model_output(repaired)

            repaired_validation = self.validate_candidate(
                markdown=repaired,
                source=source,
                language=language,
                detail_level=detail_level,
            )

            candidates.append(
                Candidate(
                    markdown=repaired,
                    validation=(repaired_validation),
                    reviewed=True,
                    retried=True,
                )
            )

            current_markdown = repaired
            current_validation = repaired_validation

            retry_count += 1

        return self.choose_best_candidate(candidates)

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
            detail_level=(detail_level),
            mode=mode,
            extra_instruction=(instruction),
        )

        initial_markdown = self.organize_initial(
            source=source,
            system_prompt=(system_prompt),
            detail_level=(detail_level),
            mode=mode,
        )

        best = self.improve_candidate(
            source=source,
            markdown=(initial_markdown),
            language=language,
            detail_level=(detail_level),
            mode=mode,
        )

        finished_at = time.perf_counter()

        return OrganizationResult(
            markdown=(best.markdown.strip()),
            reviewed=best.reviewed,
            retried=best.retried,
            processing_time=round(
                finished_at - started_at,
                3,
            ),
            input_characters=len(source),
            output_characters=len(best.markdown),
            validation=(best.validation),
        )


organizer_service = OrganizerService()

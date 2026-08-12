from __future__ import annotations

import re

from app.core.config import settings


def normalize_text(
    text: str,
) -> str:
    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    return text.strip()


def split_by_paragraphs(
    text: str,
) -> list[str]:
    normalized = normalize_text(text)

    paragraphs = re.split(
        r"\n{2,}",
        normalized,
    )

    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]


def _validate_chunk_count(
    chunks: list[str],
) -> None:
    if len(chunks) > settings.MAX_CHUNKS:
        raise ValueError(
            "Input is too large. "
            f"Maximum chunks: "
            f"{settings.MAX_CHUNKS}. "
            f"Required chunks: "
            f"{len(chunks)}."
        )


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    chunk_size = chunk_size if chunk_size is not None else settings.CHUNK_SIZE

    overlap = settings.CHUNK_OVERLAP if overlap is None else overlap

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    normalized = normalize_text(text)

    if not normalized:
        return []

    if len(normalized) <= chunk_size:
        return [normalized]

    paragraphs = split_by_paragraphs(normalized)

    chunks: list[str] = []

    current: list[str] = []

    current_length = 0

    for paragraph in paragraphs:
        paragraph_length = len(paragraph)

        if paragraph_length > chunk_size:
            if current:
                chunks.append("\n\n".join(current))

                _validate_chunk_count(chunks)

                current = []

                current_length = 0

            start = 0

            while start < paragraph_length:
                end = min(
                    start + chunk_size,
                    paragraph_length,
                )

                part = paragraph[start:end].strip()

                if part:
                    chunks.append(part)

                    _validate_chunk_count(chunks)

                if end >= paragraph_length:
                    break

                start = end - overlap

            continue

        separator_length = 2 if current else 0

        projected_length = current_length + separator_length + paragraph_length

        if projected_length > chunk_size:
            if current:
                chunks.append("\n\n".join(current))

                _validate_chunk_count(chunks)

            current = [paragraph]

            current_length = paragraph_length

        else:
            current.append(paragraph)

            current_length = projected_length

    if current:
        chunks.append("\n\n".join(current))

    final_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

    _validate_chunk_count(final_chunks)

    return final_chunks


def get_chunk_size_for_mode(
    mode: str,
) -> int:
    if mode == "fast":
        return settings.FAST_CHUNK_SIZE

    return settings.CHUNK_SIZE


def should_chunk(
    text: str,
    chunk_size: int | None = None,
) -> bool:
    if not settings.CHUNKING_ENABLED:
        return False

    effective_size = chunk_size if chunk_size is not None else settings.CHUNK_SIZE

    return len(text.strip()) > effective_size

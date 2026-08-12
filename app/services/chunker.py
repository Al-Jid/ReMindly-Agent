from __future__ import annotations

import re

from app.core.config import settings


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    return text.strip()


def split_by_paragraphs(text: str) -> list[str]:
    normalized = normalize_text(text)

    paragraphs = re.split(
        r"\n{2,}",
        normalized,
    )

    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = settings.CHUNK_OVERLAP if overlap is None else overlap

    normalized = normalize_text(text)

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

                if end >= paragraph_length:
                    break

                start = max(
                    end - overlap,
                    start + 1,
                )

            continue

        projected_length = current_length + paragraph_length + (2 if current else 0)

        if projected_length > chunk_size:
            chunks.append("\n\n".join(current))

            if overlap > 0 and chunks:
                previous = chunks[-1]

                overlap_text = previous[max(0, len(previous) - overlap) :]

                current = [
                    overlap_text,
                    paragraph,
                ]

                current_length = len(overlap_text) + len(paragraph) + 2
            else:
                current = [paragraph]
                current_length = paragraph_length

        else:
            current.append(paragraph)
            current_length = projected_length

    if current:
        chunks.append("\n\n".join(current))

    return [chunk.strip() for chunk in chunks if chunk.strip()]


def should_chunk(text: str) -> bool:
    if not settings.CHUNKING_ENABLED:
        return False

    return len(text.strip()) > settings.CHUNK_SIZE

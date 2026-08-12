import pytest

from app.core.config import settings
from app.services.chunker import (
    chunk_text,
    normalize_text,
    should_chunk,
)


def test_normalize_text():
    source = "Hello\r\nWorld\rTest"

    result = normalize_text(source)

    assert "\r" not in result
    assert result == "Hello\nWorld\nTest"


def test_small_text_returns_one_chunk():
    text = "Short text."

    chunks = chunk_text(
        text,
        chunk_size=100,
    )

    assert chunks == ["Short text."]


def test_large_text_is_split():
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."

    chunks = chunk_text(
        text,
        chunk_size=20,
        overlap=0,
    )

    assert len(chunks) > 1

    assert all(chunk.strip() for chunk in chunks)


def test_chunk_size_is_respected():
    text = "A" * 100

    chunks = chunk_text(
        text,
        chunk_size=25,
        overlap=0,
    )

    assert len(chunks) == 4

    assert all(len(chunk) <= 25 for chunk in chunks)


def test_negative_overlap_fails():
    with pytest.raises(ValueError):
        chunk_text(
            "hello",
            chunk_size=10,
            overlap=-1,
        )


def test_overlap_cannot_equal_chunk_size():
    with pytest.raises(ValueError):
        chunk_text(
            "hello world",
            chunk_size=10,
            overlap=10,
        )


def test_should_chunk_small_text():
    text = "x" * (settings.CHUNK_SIZE - 1)

    assert should_chunk(text) is False


def test_should_chunk_large_text():
    text = "x" * (settings.CHUNK_SIZE + 1)

    assert should_chunk(text) is True


def test_empty_text_returns_no_chunks():
    assert chunk_text("   ") == []

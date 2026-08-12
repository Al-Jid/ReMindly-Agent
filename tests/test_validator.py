from app.services.validator import (
    calculate_anchor_coverage,
    calculate_word_coverage,
    detect_unclosed_code_fence,
    has_markdown_heading,
    validate_markdown,
    validation_score,
)


def test_markdown_heading_detected():
    assert has_markdown_heading("# Title\nContent") is True


def test_missing_heading_detected():
    assert has_markdown_heading("Plain text only.") is False


def test_closed_code_fence():
    markdown = "```python\nprint('hello')\n```"

    assert detect_unclosed_code_fence(markdown) is False


def test_unclosed_code_fence():
    markdown = "```python\nprint('hello')"

    assert detect_unclosed_code_fence(markdown) is True


def test_word_coverage_complete():
    source = "Docker container image network"

    output = "# Notes\nDocker container image network"

    coverage = calculate_word_coverage(
        source,
        output,
    )

    assert coverage == 1.0


def test_word_coverage_partial():
    source = "Docker container image network volume"

    output = "# Notes\nDocker container"

    coverage = calculate_word_coverage(
        source,
        output,
    )

    assert 0 < coverage < 1


def test_anchor_coverage_complete():
    source = "Price is 500 and website https://example.com"

    output = "# Notes\nPrice: 500\nhttps://example.com"

    coverage = calculate_anchor_coverage(
        source,
        output,
    )

    assert coverage == 1.0


def test_empty_markdown_invalid():
    result = validate_markdown(
        markdown="",
        source_text="Hello world",
        expected_language="english",
        detail_level="medium",
    )

    assert result.valid is False

    assert any(issue.code == "empty_output" for issue in result.issues)


def test_valid_basic_markdown():
    source = "Artificial intelligence uses models and data."

    markdown = (
        "# Artificial Intelligence\n\nArtificial intelligence uses models and data."
    )

    result = validate_markdown(
        markdown=markdown,
        source_text=source,
        expected_language="english",
        detail_level="preserve",
    )

    assert result.valid is True


def test_validation_score_penalizes_errors():
    valid_result = validate_markdown(
        markdown=("# Test\n\nThis is a valid English explanation."),
        source_text=("This is a valid English explanation."),
        expected_language=("english"),
        detail_level="medium",
    )

    broken_result = validate_markdown(
        markdown=("```python\nbroken"),
        source_text=("This is source text."),
        expected_language=("english"),
        detail_level="medium",
    )

    assert validation_score(valid_result) > validation_score(broken_result)

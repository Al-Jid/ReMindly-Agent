from __future__ import annotations

import re
from dataclasses import (
    dataclass,
    field,
)

from app.services.language_detector import (
    detect_language,
    detect_language_details,
)


@dataclass
class ValidationIssueData:
    code: str

    message: str

    severity: str = "warning"


@dataclass
class MarkdownValidationResult:
    valid: bool

    issues: list[ValidationIssueData] = field(default_factory=list)


FOREIGN_SCRIPT_PATTERNS = {
    "cyrillic": re.compile(r"[\u0400-\u04FF]"),
    "cjk": re.compile(r"[\u3400-\u4DBF" r"\u4E00-\u9FFF]"),
    "hiragana": re.compile(r"[\u3040-\u309F]"),
    "katakana": re.compile(r"[\u30A0-\u30FF]"),
    "hangul": re.compile(r"[\uAC00-\uD7AF]"),
}


WORD_PATTERN = re.compile(r"[A-Za-z\u0600-\u06FF]" r"[A-Za-z0-9_\-\u0600-\u06FF]*")


NUMBER_PATTERN = re.compile(
    r"(?<!\w)" r"(?:\d+(?:[.,]\d+)*)" r"(?:%|ms|s|kg|g|cm|mm|m|GB|MB|KB)?" r"(?!\w)",
    re.IGNORECASE,
)


URL_PATTERN = re.compile(
    r"https?://[^\s)>\]]+",
    re.IGNORECASE,
)


EMAIL_PATTERN = re.compile(
    r"\b" r"[A-Za-z0-9._%+-]+" r"@" r"[A-Za-z0-9.-]+" r"\.[A-Za-z]{2,}" r"\b"
)


def has_markdown_heading(
    text: str,
) -> bool:
    return bool(
        re.search(
            r"(?m)^#{1,6}\s+\S+",
            text,
        )
    )


def detect_foreign_scripts(
    text: str,
) -> list[str]:
    found: list[str] = []

    for (
        script_name,
        pattern,
    ) in FOREIGN_SCRIPT_PATTERNS.items():
        if pattern.search(text):
            found.append(script_name)

    return found


def detect_unclosed_code_fence(
    text: str,
) -> bool:
    fences = re.findall(
        r"(?m)^```",
        text,
    )

    return len(fences) % 2 != 0


def normalize_words(
    text: str,
) -> set[str]:
    words = WORD_PATTERN.findall(text.lower())

    return {word for word in words if len(word) >= 3}


def calculate_word_coverage(
    source_text: str,
    markdown: str,
) -> float:
    source_words = normalize_words(source_text)

    output_words = normalize_words(markdown)

    if not source_words:
        return 1.0

    matched = source_words & output_words

    return len(matched) / len(source_words)


def extract_anchors(
    text: str,
) -> set[str]:
    anchors: set[str] = set()

    anchors.update(NUMBER_PATTERN.findall(text))

    anchors.update(URL_PATTERN.findall(text))

    anchors.update(EMAIL_PATTERN.findall(text))

    return {anchor.strip().lower() for anchor in anchors if anchor.strip()}


def calculate_anchor_coverage(
    source_text: str,
    markdown: str,
) -> float:
    source_anchors = extract_anchors(source_text)

    if not source_anchors:
        return 1.0

    output_lower = markdown.lower()

    found = sum(1 for anchor in source_anchors if anchor in output_lower)

    return found / len(source_anchors)


def validate_language(
    source_text: str,
    markdown: str,
    expected_language: str,
) -> list[ValidationIssueData]:
    issues: list[ValidationIssueData] = []

    output_details = detect_language_details(markdown)

    output_language = output_details.language

    if output_language == "unknown":
        return issues

    expected = expected_language

    if expected == "auto":
        expected = detect_language(source_text)

    if expected == "unknown":
        return issues

    if expected == "arabic":
        if output_details.arabic_ratio < 0.60:
            issues.append(
                ValidationIssueData(
                    code=("language_mismatch"),
                    message=(
                        "Arabic output was "
                        "expected, but the "
                        "generated text is not "
                        "predominantly Arabic."
                    ),
                    severity="error",
                )
            )

    elif expected == "english":
        if output_details.english_ratio < 0.60:
            issues.append(
                ValidationIssueData(
                    code=("language_mismatch"),
                    message=(
                        "English output was "
                        "expected, but the "
                        "generated text is not "
                        "predominantly English."
                    ),
                    severity="error",
                )
            )

    elif expected == "arabic_english":
        if not (
            output_details.arabic_ratio >= 0.08 and output_details.english_ratio >= 0.08
        ):
            issues.append(
                ValidationIssueData(
                    code=("mixed_language_missing"),
                    message=("Mixed Arabic/English output was expected."),
                    severity="warning",
                )
            )

    return issues


def validate_content_preservation(
    source_text: str,
    markdown: str,
    detail_level: str = "preserve",
) -> list[ValidationIssueData]:
    issues: list[ValidationIssueData] = []

    source_length = len(source_text.strip())

    if source_length < 100:
        return issues

    coverage_thresholds = {
        "short": {"error": 0.15, "warning": 0.25},
        "medium": {"error": 0.30, "warning": 0.45},
        "detailed": {"error": 0.45, "warning": 0.65},
        "preserve": {"error": 0.60, "warning": 0.80},
    }

    anchor_thresholds = {
        "short": {"error": 0.30, "warning": 0.50},
        "medium": {"error": 0.50, "warning": 0.70},
        "detailed": {"error": 0.70, "warning": 0.90},
        "preserve": {"error": 0.85, "warning": 1.00},
    }

    coverage_limits = coverage_thresholds.get(
        detail_level,
        coverage_thresholds["preserve"],
    )
    anchor_limits = anchor_thresholds.get(
        detail_level,
        anchor_thresholds["preserve"],
    )

    coverage = calculate_word_coverage(
        source_text,
        markdown,
    )

    if coverage < coverage_limits["error"]:
        issues.append(
            ValidationIssueData(
                code="low_content_coverage",
                message=(
                    "A large amount of source content may be missing "
                    f"for detail level '{detail_level}' "
                    f"(lexical coverage {coverage:.0%})."
                ),
                severity="error",
            )
        )
    elif coverage < coverage_limits["warning"]:
        issues.append(
            ValidationIssueData(
                code="reduced_content_coverage",
                message=(
                    "Some source content may have been omitted "
                    f"for detail level '{detail_level}' "
                    f"(lexical coverage {coverage:.0%})."
                ),
                severity="warning",
            )
        )

    anchor_coverage = calculate_anchor_coverage(
        source_text,
        markdown,
    )

    if anchor_coverage < anchor_limits["error"]:
        issues.append(
            ValidationIssueData(
                code="important_values_missing",
                message=(
                    "Some numbers, URLs, emails, or other exact values "
                    "from the source may be missing."
                ),
                severity="error",
            )
        )
    elif anchor_coverage < anchor_limits["warning"]:
        issues.append(
            ValidationIssueData(
                code="possible_values_missing",
                message=(
                    "One or more exact values from the source may not "
                    "have been preserved."
                ),
                severity="warning",
            )
        )

    return issues


def validate_expansion(
    source_text: str,
    markdown: str,
) -> list[ValidationIssueData]:
    issues: list[ValidationIssueData] = []

    source_length = len(source_text.strip())

    output_length = len(markdown.strip())

    if source_length < 100:
        return issues

    expansion_ratio = output_length / max(
        source_length,
        1,
    )

    if expansion_ratio > 4.0:
        issues.append(
            ValidationIssueData(
                code=("excessive_expansion"),
                message=(
                    "The generated output is "
                    "over four times longer "
                    "than the source and may "
                    "contain unsupported "
                    "additions."
                ),
                severity="error",
            )
        )

    elif expansion_ratio > 2.5:
        issues.append(
            ValidationIssueData(
                code=("possible_expansion"),
                message=(
                    "The generated output is "
                    "much longer than the "
                    "source. Check for "
                    "unsupported additions."
                ),
                severity="warning",
            )
        )

    return issues


def validation_score(
    result: MarkdownValidationResult,
) -> int:
    score = 100

    for issue in result.issues:
        if issue.severity == "error":
            score -= 25

        elif issue.severity == "warning":
            score -= 8

        else:
            score -= 2

    return max(
        score,
        0,
    )


def validate_markdown(
    markdown: str,
    source_text: str | None = None,
    expected_language: str = "auto",
    detail_level: str = "preserve",
) -> MarkdownValidationResult:
    issues: list[ValidationIssueData] = []

    content = markdown.strip()

    if not content:
        issues.append(
            ValidationIssueData(
                code="empty_output",
                message=("Generated Markdown is empty."),
                severity="error",
            )
        )

        return MarkdownValidationResult(
            valid=False,
            issues=issues,
        )

    if len(content) < 20:
        issues.append(
            ValidationIssueData(
                code=("suspiciously_short"),
                message=("Generated output is suspiciously short."),
                severity="warning",
            )
        )

    if not has_markdown_heading(content):
        issues.append(
            ValidationIssueData(
                code=("missing_heading"),
                message=("No Markdown heading was detected."),
                severity="warning",
            )
        )

    if detect_unclosed_code_fence(content):
        issues.append(
            ValidationIssueData(
                code=("unclosed_code_fence"),
                message=("An unclosed Markdown code fence was detected."),
                severity="error",
            )
        )

    foreign_scripts = detect_foreign_scripts(content)

    source_scripts = detect_foreign_scripts(source_text) if source_text else []

    unexpected_scripts = [
        script for script in foreign_scripts if script not in source_scripts
    ]

    if unexpected_scripts:
        issues.append(
            ValidationIssueData(
                code=("foreign_language_anomaly"),
                message=(
                    "Unexpected foreign "
                    "script detected: " + ", ".join(unexpected_scripts)
                ),
                severity="error",
            )
        )

    if source_text:
        input_length = len(source_text.strip())

        output_length = len(content)

        minimum_output_ratios = {
            "short": 0.08,
            "medium": 0.15,
            "detailed": 0.30,
            "preserve": 0.50,
        }
        minimum_output_ratio = minimum_output_ratios.get(
            detail_level,
            0.50,
        )

        if input_length > 1000 and output_length < input_length * minimum_output_ratio:
            issues.append(
                ValidationIssueData(
                    code=("possible_over_summarization"),
                    message=(
                        "Output is much shorter "
                        "than the source and may "
                        "have lost important "
                        "information."
                    ),
                    severity="warning",
                )
            )

        issues.extend(
            validate_content_preservation(
                source_text=(source_text),
                markdown=content,
                detail_level=detail_level,
            )
        )

        issues.extend(
            validate_expansion(
                source_text=(source_text),
                markdown=content,
            )
        )

        issues.extend(
            validate_language(
                source_text=(source_text),
                markdown=content,
                expected_language=(expected_language),
            )
        )

    error_exists = any(issue.severity == "error" for issue in issues)

    return MarkdownValidationResult(
        valid=not error_exists,
        issues=issues,
    )

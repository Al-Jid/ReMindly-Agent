from __future__ import annotations

import re
from dataclasses import dataclass, field


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
    "cjk": re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF]"),
    "hiragana": re.compile(r"[\u3040-\u309F]"),
    "katakana": re.compile(r"[\u30A0-\u30FF]"),
    "hangul": re.compile(r"[\uAC00-\uD7AF]"),
}


def has_markdown_heading(text: str) -> bool:
    return bool(
        re.search(
            r"(?m)^#{1,6}\s+\S+",
            text,
        )
    )


def detect_foreign_scripts(
    text: str,
) -> list[str]:
    found = []

    for script_name, pattern in FOREIGN_SCRIPT_PATTERNS.items():
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


def validate_markdown(
    markdown: str,
    source_text: str | None = None,
    expected_language: str = "auto",
) -> MarkdownValidationResult:
    issues: list[ValidationIssueData] = []

    content = markdown.strip()

    if not content:
        issues.append(
            ValidationIssueData(
                code="empty_output",
                message="Generated Markdown is empty.",
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
                code="suspiciously_short",
                message=("Generated output is suspiciously short."),
                severity="warning",
            )
        )

    if not has_markdown_heading(content):
        issues.append(
            ValidationIssueData(
                code="missing_heading",
                message=("No Markdown heading was detected."),
                severity="warning",
            )
        )

    if detect_unclosed_code_fence(content):
        issues.append(
            ValidationIssueData(
                code="unclosed_code_fence",
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
                code="foreign_language_anomaly",
                message=(
                    "Unexpected foreign script detected: "
                    + ", ".join(unexpected_scripts)
                ),
                severity="error",
            )
        )

    if source_text:
        input_length = len(source_text.strip())
        output_length = len(content)

        if input_length > 1000 and output_length < input_length * 0.15:
            issues.append(
                ValidationIssueData(
                    code="possible_over_summarization",
                    message=(
                        "Output is much shorter than "
                        "the source and may have lost "
                        "important information."
                    ),
                    severity="warning",
                )
            )

    error_exists = any(issue.severity == "error" for issue in issues)

    return MarkdownValidationResult(
        valid=not error_exists,
        issues=issues,
    )

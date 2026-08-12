from __future__ import annotations

import re
from dataclasses import dataclass

ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF]")

ENGLISH_PATTERN = re.compile(r"[A-Za-z]")


@dataclass(frozen=True)
class LanguageDetectionResult:
    language: str

    arabic_characters: int

    english_characters: int

    arabic_ratio: float

    english_ratio: float


def detect_language_details(
    text: str,
) -> LanguageDetectionResult:
    arabic_characters = len(ARABIC_PATTERN.findall(text))

    english_characters = len(ENGLISH_PATTERN.findall(text))

    total_letters = arabic_characters + english_characters

    if total_letters == 0:
        return LanguageDetectionResult(
            language="unknown",
            arabic_characters=0,
            english_characters=0,
            arabic_ratio=0.0,
            english_ratio=0.0,
        )

    arabic_ratio = arabic_characters / total_letters

    english_ratio = english_characters / total_letters

    if arabic_ratio >= 0.80:
        language = "arabic"

    elif english_ratio >= 0.80:
        language = "english"

    elif arabic_ratio >= 0.15 and english_ratio >= 0.15:
        language = "arabic_english"

    elif arabic_ratio > english_ratio:
        language = "arabic"

    else:
        language = "english"

    return LanguageDetectionResult(
        language=language,
        arabic_characters=(arabic_characters),
        english_characters=(english_characters),
        arabic_ratio=round(
            arabic_ratio,
            4,
        ),
        english_ratio=round(
            english_ratio,
            4,
        ),
    )


def detect_language(
    text: str,
) -> str:
    return detect_language_details(text).language

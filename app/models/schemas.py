from typing import Literal

from pydantic import BaseModel, Field

MAX_INPUT_CHARACTERS = 100_000
MAX_INSTRUCTION_CHARACTERS = 2_000


ProcessingMode = Literal[
    "fast",
    "balanced",
    "quality",
]

LanguageMode = Literal[
    "auto",
    "arabic",
    "english",
    "arabic_english",
]

DetailLevel = Literal[
    "short",
    "medium",
    "detailed",
    "preserve",
]


class OrganizeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=MAX_INPUT_CHARACTERS,
        description="Raw explanation to organize",
    )

    instruction: str | None = Field(
        default=None,
        max_length=MAX_INSTRUCTION_CHARACTERS,
        description="Optional custom instruction",
    )

    mode: ProcessingMode = Field(
        default="balanced",
    )

    language: LanguageMode = Field(
        default="auto",
    )

    detail_level: DetailLevel = Field(
        default="preserve",
    )


class ValidationIssue(BaseModel):
    code: str

    message: str

    severity: Literal[
        "info",
        "warning",
        "error",
    ]


class ValidationResult(BaseModel):
    valid: bool

    issues: list[ValidationIssue] = Field(
        default_factory=list,
    )


class OrganizeResponse(BaseModel):
    markdown: str

    mode: ProcessingMode

    language: LanguageMode

    detail_level: DetailLevel

    reviewed: bool = False

    processing_time: float

    input_characters: int

    output_characters: int

    validation: ValidationResult | None = None


class ErrorResponse(BaseModel):
    detail: str

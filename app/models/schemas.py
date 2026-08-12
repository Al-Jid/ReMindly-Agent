from typing import Literal, Optional

from pydantic import BaseModel, Field

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
        description="Raw explanation to organize",
    )

    instruction: Optional[str] = Field(
        default=None,
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

    issues: list[ValidationIssue] = []


class OrganizeResponse(BaseModel):
    markdown: str

    mode: ProcessingMode

    language: LanguageMode

    detail_level: DetailLevel

    reviewed: bool = False

    processing_time: float

    input_characters: int

    output_characters: int

    validation: Optional[ValidationResult] = None


class ErrorResponse(BaseModel):
    detail: str

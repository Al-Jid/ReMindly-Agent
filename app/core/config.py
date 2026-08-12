import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # =========================================================
    # AI Provider
    # =========================================================

    API_KEY: str = os.getenv(
        "MODEL_API_KEY",
        "",
    )

    BASE_URL: str = os.getenv(
        "MODEL_BASE_URL",
        "https://openrouter.ai/api/v1",
    )

    MODEL_NAME: str = os.getenv(
        "MODEL_NAME",
        "nvidia/nemotron-3-super-120b-a12b:free",
    )

    # =========================================================
    # LLM
    # =========================================================

    TEMPERATURE: float = float(
        os.getenv(
            "MODEL_TEMPERATURE",
            "0.2",
        )
    )

    TIMEOUT_SECONDS: int = int(
        os.getenv(
            "MODEL_TIMEOUT",
            "90",
        )
    )

    MAX_OUTPUT_TOKENS: int = int(
        os.getenv(
            "MAX_OUTPUT_TOKENS",
            "8000",
        )
    )

    MAX_GENERATION_RETRIES: int = int(
        os.getenv(
            "MAX_GENERATION_RETRIES",
            "1",
        )
    )

    # =========================================================
    # Performance
    # =========================================================

    FAST_SINGLE_PASS_MAX_CHARS: int = int(
        os.getenv(
            "FAST_SINGLE_PASS_MAX_CHARS",
            "16000",
        )
    )

    MAX_PARALLEL_CHUNKS: int = int(
        os.getenv(
            "MAX_PARALLEL_CHUNKS",
            "3",
        )
    )

    # =========================================================
    # Chunking
    # =========================================================

    CHUNKING_ENABLED: bool = (
        os.getenv(
            "CHUNKING_ENABLED",
            "true",
        ).lower()
        == "true"
    )

    CHUNK_SIZE: int = int(
        os.getenv(
            "CHUNK_SIZE",
            "12000",
        )
    )

    FAST_CHUNK_SIZE: int = int(
        os.getenv(
            "FAST_CHUNK_SIZE",
            "18000",
        )
    )

    CHUNK_OVERLAP: int = int(
        os.getenv(
            "CHUNK_OVERLAP",
            "0",
        )
    )

    MAX_CHUNKS: int = int(
        os.getenv(
            "MAX_CHUNKS",
            "10",
        )
    )

    # =========================================================
    # API protection
    # =========================================================

    APP_API_KEY: str = os.getenv(
        "APP_API_KEY",
        "",
    )

    # =========================================================
    # Rate limiting
    # =========================================================

    ORGANIZE_RATE_LIMIT: str = os.getenv(
        "ORGANIZE_RATE_LIMIT",
        "10/minute",
    )

    STREAM_RATE_LIMIT: str = os.getenv(
        "STREAM_RATE_LIMIT",
        "5/minute",
    )

    # =========================================================
    # Application
    # =========================================================

    APP_NAME: str = "ReMindly Agent"

    APP_VERSION: str = "2.2.1"

    # =========================================================
    # Output Budgets
    # =========================================================

    @classmethod
    def output_token_budget(
        cls,
        detail_level: str,
        mode: str,
    ) -> int:
        detail_budgets = {
            "short": 2600,
            "medium": 3800,
            "detailed": 6000,
            "preserve": (cls.MAX_OUTPUT_TOKENS),
        }

        budget = detail_budgets.get(
            detail_level,
            cls.MAX_OUTPUT_TOKENS,
        )

        if mode == "fast":
            fast_caps = {
                "short": 2400,
                "medium": 3400,
                "detailed": 5000,
                "preserve": 6500,
            }

            budget = min(
                budget,
                fast_caps.get(
                    detail_level,
                    6500,
                ),
            )

        return min(
            budget,
            cls.MAX_OUTPUT_TOKENS,
        )

    @classmethod
    def chunk_output_token_budget(
        cls,
        detail_level: str,
        mode: str,
    ) -> int:
        final_budget = cls.output_token_budget(
            detail_level,
            mode,
        )

        if detail_level == "short":
            return min(
                1500,
                final_budget,
            )

        if detail_level == "medium":
            return min(
                2200,
                final_budget,
            )

        if detail_level == "detailed":
            return min(
                3200,
                final_budget,
            )

        return min(
            4000,
            final_budget,
        )

    # =========================================================
    # Validation
    # =========================================================

    @classmethod
    def validate(cls) -> None:
        errors: list[str] = []

        if not cls.API_KEY:
            errors.append("MODEL_API_KEY is missing")

        if not cls.BASE_URL:
            errors.append("MODEL_BASE_URL is missing")

        if not cls.MODEL_NAME:
            errors.append("MODEL_NAME is missing")

        if cls.TIMEOUT_SECONDS <= 0:
            errors.append("MODEL_TIMEOUT must be greater than 0")

        if not (0.0 <= cls.TEMPERATURE <= 2.0):
            errors.append("MODEL_TEMPERATURE must be between 0 and 2")

        if cls.MAX_OUTPUT_TOKENS <= 0:
            errors.append("MAX_OUTPUT_TOKENS must be greater than 0")

        if cls.MAX_GENERATION_RETRIES < 0:
            errors.append("MAX_GENERATION_RETRIES cannot be negative")

        if cls.CHUNK_SIZE <= 0:
            errors.append("CHUNK_SIZE must be greater than 0")

        if cls.FAST_CHUNK_SIZE <= 0:
            errors.append("FAST_CHUNK_SIZE must be greater than 0")

        if cls.FAST_SINGLE_PASS_MAX_CHARS <= 0:
            errors.append("FAST_SINGLE_PASS_MAX_CHARS must be greater than 0")

        if cls.MAX_PARALLEL_CHUNKS <= 0:
            errors.append("MAX_PARALLEL_CHUNKS must be greater than 0")

        if cls.CHUNK_OVERLAP < 0:
            errors.append("CHUNK_OVERLAP cannot be negative")

        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            errors.append("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")

        if cls.MAX_CHUNKS <= 0:
            errors.append("MAX_CHUNKS must be greater than 0")

        if errors:
            raise RuntimeError("Configuration error: " + ", ".join(errors))


settings = Settings()

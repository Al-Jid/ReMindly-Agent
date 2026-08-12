import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # AI Provider
    API_KEY: str = os.getenv("MODEL_API_KEY", "")
    BASE_URL: str = os.getenv(
        "MODEL_BASE_URL",
        "https://openrouter.ai/api/v1",
    )
    MODEL_NAME: str = os.getenv(
        "MODEL_NAME",
        "nvidia/nemotron-3-super-120b-a12b:free",
    )

    # LLM
    TEMPERATURE: float = float(os.getenv("MODEL_TEMPERATURE", "0.2"))

    TIMEOUT_SECONDS: int = int(os.getenv("MODEL_TIMEOUT", "90"))

    # Chunking
    CHUNKING_ENABLED: bool = os.getenv("CHUNKING_ENABLED", "true").lower() == "true"

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "12000"))

    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "500"))

    # Application
    APP_NAME: str = "MD Notes Agent"
    APP_VERSION: str = "2.0.0"

    @classmethod
    def validate(cls):
        errors = []

        if not cls.API_KEY:
            errors.append("MODEL_API_KEY is missing")

        if not cls.BASE_URL:
            errors.append("MODEL_BASE_URL is missing")

        if not cls.MODEL_NAME:
            errors.append("MODEL_NAME is missing")

        if errors:
            raise RuntimeError("Configuration error: " + ", ".join(errors))


settings = Settings()

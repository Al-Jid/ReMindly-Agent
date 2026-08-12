from __future__ import annotations

import re
from collections.abc import Generator

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)

from app.core.config import settings

META_PREFIX_PATTERNS = (
    r"^\s*we need to\b",
    r"^\s*we need\b",
    r"^\s*we should\b",
    r"^\s*let(?:'s| us)\b",
    r"^\s*the user\b",
    r"^\s*i need to\b",
    r"^\s*i should\b",
    r"^\s*our task\b",
    r"^\s*the task\b",
    r"^\s*analysis\b",
    r"^\s*reasoning\b",
)


def clean_model_output(
    content: str,
) -> str:
    text = content.strip()

    if text.startswith("```markdown") and text.endswith("```"):
        text = text[len("```markdown") : -3].strip()

    elif text.startswith("```md") and text.endswith("```"):
        text = text[len("```md") : -3].strip()

    # Some reasoning models occasionally expose
    # planning text before the actual Markdown.
    heading_match = re.search(
        r"(?m)^#{1,6}\s+\S+",
        text,
    )

    if heading_match:
        prefix = text[: heading_match.start()].strip()

        if prefix:
            prefix_lower = prefix.lower()

            has_meta_prefix = any(
                re.search(
                    pattern,
                    prefix_lower,
                    re.IGNORECASE,
                )
                for pattern in META_PREFIX_PATTERNS
            )

            if has_meta_prefix:
                text = text[heading_match.start() :]

    return text.strip()


class LLMService:
    def __init__(
        self,
    ) -> None:
        settings.validate()

        self.client = OpenAI(
            api_key=settings.API_KEY,
            base_url=settings.BASE_URL,
            timeout=settings.TIMEOUT_SECONDS,
            max_retries=1,
        )

        self.model = settings.MODEL_NAME

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        try:
            token_limit = (
                max_tokens if max_tokens is not None else settings.MAX_OUTPUT_TOKENS
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (system_prompt),
                    },
                    {
                        "role": "user",
                        "content": (user_prompt),
                    },
                ],
                temperature=(
                    settings.TEMPERATURE if temperature is None else temperature
                ),
                max_tokens=(token_limit),
            )

            if not response.choices:
                raise RuntimeError("The model returned no choices.")

            content = response.choices[0].message.content

            if not content:
                raise RuntimeError("The model returned an empty response.")

            cleaned = clean_model_output(content)

            if not cleaned:
                raise RuntimeError("The model returned no usable content.")

            return cleaned

        except RateLimitError as exc:
            raise RuntimeError("The AI provider is currently rate limited.") from exc

        except APITimeoutError as exc:
            raise RuntimeError(
                f"The AI request exceeded {settings.TIMEOUT_SECONDS} seconds."
            ) from exc

        except APIConnectionError as exc:
            raise RuntimeError("Could not connect to the AI provider.") from exc

        except APIStatusError as exc:
            raise RuntimeError(
                f"The AI provider returned HTTP {exc.status_code}."
            ) from exc

        except RuntimeError:
            raise

        except Exception as exc:
            raise RuntimeError("Unexpected AI provider error.") from exc

    def stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> Generator[
        str,
        None,
        None,
    ]:
        try:
            token_limit = (
                max_tokens if max_tokens is not None else settings.MAX_OUTPUT_TOKENS
            )

            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (system_prompt),
                    },
                    {
                        "role": "user",
                        "content": (user_prompt),
                    },
                ],
                temperature=(
                    settings.TEMPERATURE if temperature is None else temperature
                ),
                max_tokens=(token_limit),
                stream=True,
            )

            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                if delta.content:
                    yield delta.content

        except RateLimitError as exc:
            raise RuntimeError("The AI provider is currently rate limited.") from exc

        except APITimeoutError as exc:
            raise RuntimeError(
                f"The AI request exceeded {settings.TIMEOUT_SECONDS} seconds."
            ) from exc

        except APIConnectionError as exc:
            raise RuntimeError("Could not connect to the AI provider.") from exc

        except APIStatusError as exc:
            raise RuntimeError(
                f"The AI provider returned HTTP {exc.status_code}."
            ) from exc

        except RuntimeError:
            raise

        except Exception as exc:
            raise RuntimeError("Unexpected AI streaming error.") from exc

    def configuration_status(
        self,
    ) -> dict[str, bool]:
        return {
            "api_key_configured": (bool(settings.API_KEY)),
            "base_url_configured": (bool(settings.BASE_URL)),
            "model_configured": (bool(settings.MODEL_NAME)),
        }


llm_service = LLMService()

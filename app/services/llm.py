from __future__ import annotations

from collections.abc import Generator

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)

from app.core.config import settings


class LLMService:
    def __init__(self) -> None:
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
    ) -> str:
        """
        Generate a normal non-streaming response.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=(
                    settings.TEMPERATURE if temperature is None else temperature
                ),
            )

            content = response.choices[0].message.content

            if not content:
                raise RuntimeError("The model returned an empty response.")

            return content.strip()

        except RateLimitError as exc:
            raise RuntimeError(
                "The model is currently rate limited. Please retry shortly."
            ) from exc

        except APITimeoutError as exc:
            raise RuntimeError(
                f"The AI request exceeded {settings.TIMEOUT_SECONDS} seconds."
            ) from exc

        except APIConnectionError as exc:
            raise RuntimeError("Could not connect to the AI provider.") from exc

        except APIStatusError as exc:
            raise RuntimeError(
                f"AI provider returned HTTP {exc.status_code}: {exc.message}"
            ) from exc

        except Exception as exc:
            raise RuntimeError(f"Unexpected AI error: {exc}") from exc

    def stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> Generator[str, None, None]:
        """
        Stream generated text chunk-by-chunk.

        The frontend will later receive these chunks live.
        """

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=(
                    settings.TEMPERATURE if temperature is None else temperature
                ),
                stream=True,
            )

            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                if delta.content:
                    yield delta.content

        except RateLimitError as exc:
            raise RuntimeError("The model is currently rate limited.") from exc

        except APITimeoutError as exc:
            raise RuntimeError(
                f"The AI request exceeded {settings.TIMEOUT_SECONDS} seconds."
            ) from exc

        except APIConnectionError as exc:
            raise RuntimeError("Could not connect to the AI provider.") from exc

        except APIStatusError as exc:
            raise RuntimeError(
                f"AI provider returned HTTP {exc.status_code}: {exc.message}"
            ) from exc

        except Exception as exc:
            raise RuntimeError(f"Unexpected AI streaming error: {exc}") from exc


llm_service = LLMService()

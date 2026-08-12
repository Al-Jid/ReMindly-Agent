from __future__ import annotations

from app.core.prompts import build_review_prompt
from app.services.llm import llm_service


class ReviewerService:
    def review(
        self,
        source_text: str,
        generated_markdown: str,
    ) -> str:
        system_prompt = build_review_prompt()

        user_prompt = f"""
ORIGINAL SOURCE:

{source_text}

---

GENERATED MARKDOWN:

{generated_markdown}
""".strip()

        return llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
        )


reviewer_service = ReviewerService()

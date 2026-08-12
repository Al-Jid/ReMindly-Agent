from __future__ import annotations

from app.core.prompts import (
    build_review_prompt,
)
from app.services.llm import (
    llm_service,
)


class ReviewerService:
    def review(
        self,
        source_text: str,
        generated_markdown: str,
        expected_language: str = "auto",
        detail_level: str = "preserve",
    ) -> str:
        system_prompt = build_review_prompt()

        user_prompt = f"""
Review and repair the generated Markdown using the ORIGINAL SOURCE as the source of truth.

STRICT RULES:
- Do not add new facts.
- Do not infer facts that are not explicitly supported by the source.
- Restore important source information that was omitted.
- Remove claims that are not supported by the source.
- Preserve names exactly where possible.
- Preserve numbers, dates, percentages, URLs, emails, commands, code, and technical terms.
- Preserve the original meaning.
- Keep clean Markdown formatting.
- Avoid duplicate sections and duplicate headings.
- Do not mention that you reviewed the document.
- Return only the corrected Markdown.

EXPECTED LANGUAGE:
{expected_language}

DETAIL LEVEL:
{detail_level}

ORIGINAL SOURCE:

{source_text}

---

GENERATED MARKDOWN:

{generated_markdown}
""".strip()

        result = llm_service.generate(
            system_prompt=(system_prompt),
            user_prompt=(user_prompt),
            temperature=0.1,
        )

        result = result.strip()

        if not result:
            raise RuntimeError("Quality review returned an empty result.")

        return result

    def repair(
        self,
        source_text: str,
        generated_markdown: str,
        validation_messages: list[str],
        expected_language: str = "auto",
        detail_level: str = "preserve",
    ) -> str:
        system_prompt = build_review_prompt()

        problems = "\n".join(f"- {message}" for message in validation_messages)

        user_prompt = f"""
Repair the Markdown below.

The current version failed validation.

VALIDATION PROBLEMS:

{problems}

STRICT RULES:
- Fix the validation problems.
- Use ONLY information supported by the original source.
- Restore omitted source information.
- Remove unsupported additions.
- Preserve all names, numbers, dates, URLs, emails, commands, code, and technical terms.
- Do not introduce new facts.
- Do not unnecessarily rewrite content that is already correct.
- Keep clean Markdown.
- Return only the repaired Markdown.

EXPECTED LANGUAGE:
{expected_language}

DETAIL LEVEL:
{detail_level}

ORIGINAL SOURCE:

{source_text}

---

MARKDOWN TO REPAIR:

{generated_markdown}
""".strip()

        result = llm_service.generate(
            system_prompt=(system_prompt),
            user_prompt=(user_prompt),
            temperature=0.05,
        )

        result = result.strip()

        if not result:
            raise RuntimeError("Repair returned an empty result.")

        return result


reviewer_service = ReviewerService()

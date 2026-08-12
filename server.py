from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="MD Notes Agent")

app.mount("/static", StaticFiles(directory="static"), name="static")


class OrganizeRequest(BaseModel):
    text: str
    instruction: str | None = None


SYSTEM_PROMPT = """
You are a Markdown Notes Organizer.

Transform raw explanatory text into clean, logically structured Markdown.

Rules:
- Preserve the original meaning and facts.
- Do not invent missing information.
- Remove filler and unnecessary repetition.
- Keep the input language unless explicitly asked otherwise.
- Use #, ##, and ### headings appropriately.
- Use bullets for related points.
- Use numbered lists only when order matters.
- Use tables only when they genuinely improve a comparison.
- Format code, commands, file paths, formulas, and technical identifiers correctly.
- Make the result easy to study and scan.
- Return ONLY Markdown.
- Do not wrap the entire response in a code fence.
""".strip()


def get_client() -> OpenAI:
    api_key = os.getenv("MODEL_API_KEY")
    base_url = os.getenv("MODEL_BASE_URL")

    if not api_key:
        raise RuntimeError("MODEL_API_KEY is missing.")

    kwargs = {"api_key": api_key}

    if base_url:
        kwargs["base_url"] = base_url

    return OpenAI(**kwargs)


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.post("/api/organize")
def organize(payload: OrganizeRequest):
    text = payload.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    model = os.getenv("MODEL_NAME")

    if not model:
        raise HTTPException(status_code=500, detail="MODEL_NAME is missing in .env.")

    prompt = f"Organize this explanation into Markdown notes:\n\n{text}"

    if payload.instruction:
        prompt += f"\n\nAdditional instruction:\n{payload.instruction.strip()}"

    try:
        client = get_client()

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        markdown = response.choices[0].message.content

        if not markdown:
            raise RuntimeError("The model returned an empty response.")

        return {"markdown": markdown.strip()}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

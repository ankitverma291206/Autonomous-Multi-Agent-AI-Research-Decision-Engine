"""Demo and OpenAI-compatible structured report generation."""

import json

import httpx
from pydantic import ValidationError

from research_engine.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_PROVIDER
from research_engine.schemas import Confidence

EVIDENCE_NOTICE = (
    "Preliminary AI-generated analysis. No external sources were searched or verified; "
    "check all factual claims before using this report to make a decision."
)


class LLMUnavailable(Exception):
    pass


class LLMResponseError(Exception):
    pass


def demo_report(query: str) -> dict:
    """Return a deterministic no-credentials-needed report for the end-to-end demo."""
    return {
        "summary": f"This is a preliminary decision brief for: {query}",
        "recommendation": (
            "Treat this as a research question to validate. Define decision criteria, gather current "
            "primary-source evidence, and compare realistic scenarios before committing resources."
        ),
        "key_factors": [
            "Expected costs, benefits, and time horizon",
            "Available alternatives and opportunity cost",
            "Operational, regulatory, and market uncertainty",
        ],
        "assumptions": ["The question is exploratory and no supporting documents were provided."],
        "risks": ["No external research or source verification has been performed."],
        "confidence": Confidence.low.value,
    }


async def generate_report(query: str) -> tuple[dict, str]:
    if LLM_PROVIDER == "demo":
        return demo_report(query), "demo"
    if LLM_PROVIDER != "openai_compatible":
        raise LLMUnavailable("Set LLM_PROVIDER to 'demo' or 'openai_compatible'.")
    if not LLM_API_KEY:
        raise LLMUnavailable("LLM_API_KEY is required when using the configured LLM provider.")

    prompt = (
        "Create a concise preliminary decision brief for the user's question. You have not browsed "
        "the web and have no source documents. Do not invent statistics, named sources, or citations. "
        "Keep confidence low unless the question can be answered from the question alone. Return JSON "
        "with exactly these fields: summary (string), recommendation (string), key_factors (array of "
        "2-6 strings), assumptions (array of up to 6 strings), risks (array of up to 6 strings), "
        "confidence (low, medium, or high).\n\nQuestion: " + query
    )
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, connect=10.0)) as client:
            response = await client.post(
                f"{LLM_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {LLM_API_KEY}"},
                json={
                    "model": LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2,
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            # Validate the model-controlled fields before returning them to the API.
            from research_engine.schemas import LLMReportContent

            validated = LLMReportContent.model_validate(parsed)
            return validated.model_dump(mode="json"), "llm"
    except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError, ValidationError) as exc:
        raise LLMResponseError("The model provider returned an unavailable or invalid response.") from exc

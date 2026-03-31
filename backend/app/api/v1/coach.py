"""Coach API — AI-powered contextual coaching via Groq LLM."""

from typing import Any

from fastapi import APIRouter, Depends

from app.dependencies import require_role
from app.models.user import UserRole
from app.services.llm import ask_analysis, ask_coach

router = APIRouter(dependencies=[Depends(require_role(UserRole.UTILISATEUR))])


@router.post("")
async def get_coach_advice(
    body: dict[str, Any],
) -> dict[str, str | None]:
    """Return AI coaching advice for the given page context."""
    page = body.get("page", "unknown")
    context = body.get("context", {})

    advice = await ask_coach(page=page, context_data=context)

    return {"advice": advice}


@router.post("/analyze")
async def analyze_data(
    body: dict[str, Any],
) -> dict[str, str | None]:
    """Return AI expert analysis for a specific topic.

    Body example:
    {
        "topic": "grid" | "statistics" | "portfolio" | "simulation" | "dashboard",
        "context": { ... topic-specific data ... }
    }
    """
    topic = body.get("topic", "dashboard")
    context = body.get("context", {})

    advice = await ask_analysis(topic=topic, context_data=context)
    return {"advice": advice}

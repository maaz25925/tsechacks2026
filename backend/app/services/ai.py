from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.config import get_settings


class AIService:
    """
    Groq-first, OpenAI fallback.

    Both are OpenAI-compatible, so we use the same SDK and swap base_url + api_key.
    """

    def __init__(self) -> None:
        s = get_settings()
        self._groq = (
            OpenAI(api_key=s.groq_api_key, base_url=s.groq_base_url) if s.groq_api_key else None
        )
        self._openai = (
            OpenAI(api_key=s.openai_api_key, base_url=s.openai_base_url)
            if s.openai_api_key
            else None
        )
        self._model = s.ai_model
        self._fallback_model = s.openai_fallback_model

    def _chat_json(
        self,
        *,
        system: str,
        user: str,
        schema_hint: str,
    ) -> dict[str, Any]:
        """
        Ask the model to return strict JSON. If it returns non-JSON, we best-effort parse.
        """
        prompt = (
            f"{user}\n\n"
            "Return ONLY valid JSON. No markdown.\n"
            f"JSON schema (informal): {schema_hint}\n"
        )

        last_err: Exception | None = None
        for client, model in [
            (self._groq, self._model),
            (self._openai, self._fallback_model),
        ]:
            if client is None:
                continue
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                content = (resp.choices[0].message.content or "").strip()
                return json.loads(content)
            except Exception as e:  # noqa: BLE001 - we want fallback behavior
                last_err = e
                continue

        raise last_err or RuntimeError("AI client not configured")

    def suggest_listings(
        self,
        *,
        query: str,
        listings: list[dict[str, Any]],
    ) -> tuple[list[str], str | None]:
        """
        Returns (listing_ids, reasoning).
        """
        system = (
            "You are Murph, an AI course concierge. "
            "Pick the best 2-3 listings for the student's query."
        )
        user = (
            f"Student query: {query}\n\n"
            "Available listings (JSON array):\n"
            f"{json.dumps(listings, ensure_ascii=False)}"
        )
        schema_hint = '{ "listing_ids": ["..."], "reasoning": "..." }'
        data = self._chat_json(system=system, user=user, schema_hint=schema_hint)
        ids = [str(x) for x in (data.get("listing_ids") or [])][:3]
        reasoning = data.get("reasoning")
        return ids, reasoning

    def score_review_credibility(
        self,
        *,
        rating: int,
        review_text: str,
        engagement_metrics: dict[str, Any] | None,
        completion_percentage: float,
        duration_min: float,
    ) -> tuple[float, int]:
        """
        Returns (credibility_score 0..1, bonus_percentage 0..15).

        Bonus rules:
        - Only apply if rating >= 4 AND credibility is high.
        - If credibility >= 0.85 => 15%
        - If credibility >= 0.70 => 10%
        - If credibility >= 0.55 => 5%
        Otherwise 0.
        """
        system = (
            "You are an integrity validator for course reviews. "
            "Use engagement metrics to estimate whether the review is credible. "
            "Low engagement, excessive skipping, or tiny completion should reduce credibility."
        )
        user = (
            "Compute a credibility score (0..1) for this review.\n"
            f"rating: {rating}\n"
            f"review_text: {review_text}\n"
            f"completion_percentage: {completion_percentage}\n"
            f"duration_min: {duration_min}\n"
            f"engagement_metrics: {json.dumps(engagement_metrics or {}, ensure_ascii=False)}\n"
        )
        schema_hint = '{ "credibility_score": 0.0 }'
        data = self._chat_json(system=system, user=user, schema_hint=schema_hint)

        try:
            score = float(data.get("credibility_score"))
        except Exception:
            score = 0.0
        score = max(0.0, min(1.0, score))

        bonus = 0
        if rating >= 4:
            if score >= 0.85:
                bonus = 15
            elif score >= 0.70:
                bonus = 10
            elif score >= 0.55:
                bonus = 5
        return score, bonus


_ai: AIService | None = None


def get_ai() -> AIService:
    global _ai
    if _ai is None:
        _ai = AIService()
    return _ai


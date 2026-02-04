from __future__ import annotations

import json
from typing import Any

import pandas as pd
from openai import OpenAI
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

from app.config import get_settings
from app.supabase_client import SupabaseService


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

    # ---------- Time-series utilities (ARIMA) ----------
    def _build_series(
        self,
        rows: list[dict[str, Any]],
        value_key: str,
    ) -> pd.Series:
        """
        Build a pandas Series indexed by created_at for ARIMA.
        """
        if not rows:
            return pd.Series(dtype="float64")
        df = pd.DataFrame(
            [
                {
                    "created_at": r.get("created_at"),
                    "value": float(r.get(value_key) or 0.0),
                }
                for r in rows
                if r.get("created_at") is not None
            ]
        )
        if df.empty:
            return pd.Series(dtype="float64")
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")
        df = df.dropna(subset=["created_at"]).sort_values("created_at")
        df = df.set_index("created_at")
        return df["value"]

    def _fit_arima_and_forecast(
        self,
        series: pd.Series,
        steps: int = 3,
    ) -> list[float]:
        """
        Fit a very small ARIMA model and forecast `steps` ahead.
        Falls back to mean when series is too short or model fails.
        """
        if len(series) < 5:
            mean_val = float(series.mean()) if len(series) else 0.0
            return [round(mean_val, 3)] * steps

        y = series.astype("float64")
        d = 0
        try:
            adf_p = adfuller(y)[1]
            if adf_p > 0.05:
                d = 1
        except Exception:
            d = 0

        try:
            model = ARIMA(y, order=(1, d, 1))
            fitted = model.fit()
            forecast = fitted.forecast(steps=steps)
            return [round(float(v), 3) for v in forecast.tolist()]
        except Exception:
            mean_val = float(y.mean()) if len(y) else 0.0
            return [round(mean_val, 3)] * steps

    def forecast_bonus(
        self,
        teacher_id: str,
        db: SupabaseService,
        steps: int = 3,
    ) -> dict[str, Any]:
        """
        Forecast future bonus_percentage for a teacher using ARIMA.

        Frontend usage (teacher dashboard):
        - Show avg_forecast_bonus and small sparkline of next_bonus_predictions.
        """
        # Collect all reviews for sessions taught by this teacher
        sessions = (
            db.client.table("sessions")
            .select("id")
            .eq("teacher_id", teacher_id)
            .eq("status", "ended")
            .execute()
            .data
            or []
        )
        session_ids = [s["id"] for s in sessions]
        if not session_ids:
            return {
                "avg_forecast_bonus": 0.0,
                "next_bonus_predictions": [0.0] * steps,
            }

        reviews = (
            db.client.table("reviews")
            .select("session_id,bonus_percentage,created_at")
            .in_("session_id", session_ids)
            .order("created_at", desc=False)
            .execute()
            .data
            or []
        )
        series = self._build_series(reviews, "bonus_percentage")
        forecast = self._fit_arima_and_forecast(series, steps=steps)
        avg_forecast = round(sum(forecast) / len(forecast), 3) if forecast else 0.0
        return {
            "avg_forecast_bonus": avg_forecast,
            "next_bonus_predictions": forecast,
        }

    def validate_review_with_arima(
        self,
        session_id: str,
        rating: int,
        db: SupabaseService,
    ) -> dict[str, Any]:
        """
        Detect anomalies in ratings using ARIMA on historical ratings per teacher.

        Returns:
        - anomaly_score: 0..1 (higher = more anomalous)
        - predicted_rating: float
        """
        session = db.maybe_single("sessions", "*", id=session_id)
        if not session:
            return {"anomaly_score": 0.0, "predicted_rating": float(rating)}

        teacher_id = session.get("teacher_id")
        if not teacher_id:
            return {"anomaly_score": 0.0, "predicted_rating": float(rating)}

        sessions = (
            db.client.table("sessions")
            .select("id")
            .eq("teacher_id", teacher_id)
            .eq("status", "ended")
            .execute()
            .data
            or []
        )
        session_ids = [s["id"] for s in sessions]
        if not session_ids:
            return {"anomaly_score": 0.0, "predicted_rating": float(rating)}

        reviews = (
            db.client.table("reviews")
            .select("session_id,rating,created_at")
            .in_("session_id", session_ids)
            .order("created_at", desc=False)
            .execute()
            .data
            or []
        )
        series = self._build_series(reviews, "rating")
        forecast_list = self._fit_arima_and_forecast(series, steps=1)
        predicted = forecast_list[0] if forecast_list else float(rating)

        # ratings are 1-5, normalize deviation to 0..1
        max_range = 4.0
        deviation = abs(float(rating) - float(predicted))
        anomaly = max(0.0, min(1.0, deviation / max_range))
        return {"anomaly_score": round(anomaly, 3), "predicted_rating": round(predicted, 3)}


_ai: AIService | None = None


def get_ai() -> AIService:
    global _ai
    if _ai is None:
        _ai = AIService()
    return _ai


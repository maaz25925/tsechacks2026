from __future__ import annotations

from typing import Any


def compute_completion_percentage(listing: dict[str, Any], engagement: dict[str, Any] | None) -> float:
    """
    MVP completion computation.

    Frontend can send either:
    - completion_percentage directly, OR
    - chunk-based metrics:
        engagement_metrics = {
          "total_chunks": 120,
          "viewed_chunks": [0,1,2,5,...],  # unique viewed chunk indices
          "rewatched_chunks": [2,3],       # optional
          "skipped_chunks": [10,11],       # optional
        }

    For edge cases (skips/rewatches), we only count unique viewed chunks.
    """
    if not engagement:
        return 0.0
    total = engagement.get("total_chunks")
    viewed = engagement.get("viewed_chunks")
    if isinstance(total, int) and total > 0 and isinstance(viewed, list):
        unique = len(set(int(x) for x in viewed if isinstance(x, (int, float, str))))
        pct = (unique / total) * 100.0
        return max(0.0, min(100.0, pct))

    # fallback: if frontend provides something else, ignore
    return 0.0


def compute_charge_amount(
    *,
    duration_min: float,
    completion_percentage: float,
    price_per_min: float,
    total_duration_min: float,
    reserve_amount: float,
) -> tuple[float, float]:
    """
    Charge model:
    - Base usage is driven by time watched, capped by listing total duration.
    - completion_percentage acts as a trust signal to avoid charging full amount
      if the user skipped around (low completion).

    We compute an "effective watched minutes":
        watched = min(duration_min, total_duration_min)
        engagement_factor = clamp(completion_percentage/100, 0..1)
        effective_minutes = watched * (0.5 + 0.5*engagement_factor)

    Then:
        computed = effective_minutes * price_per_min
        final_charge = min(reserve_amount, computed)
        refund = reserve_amount - final_charge
    """
    watched = max(0.0, min(duration_min, total_duration_min))
    engagement_factor = max(0.0, min(1.0, completion_percentage / 100.0))
    effective_minutes = watched * (0.5 + 0.5 * engagement_factor)

    computed = max(0.0, effective_minutes * price_per_min)
    final_charge = min(reserve_amount, computed)
    refund = max(0.0, reserve_amount - final_charge)
    return round(final_charge, 2), round(refund, 2)


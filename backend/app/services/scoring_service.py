"""
SoukAI Scoring Service
Computes a final trend score (0–100) from product metrics using a weighted formula.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scoring weights (must sum to 1.0)
# ---------------------------------------------------------------------------

WEIGHT_PURCHASE_INTENT = 0.35
WEIGHT_TREND_GROWTH = 0.25
WEIGHT_COMMENT_VOLUME = 0.15
WEIGHT_PROFIT_MARGIN = 0.15
WEIGHT_COMPETITION = 0.10   # inverted: low competition → high score

# Comment volume normalisation cap
COMMENT_VOLUME_CAP = 100


def compute_trend_score(
    purchase_intent_score: float,
    trend_growth: float,
    comment_volume: int,
    profit_margin: float,
    competition_level: float,
) -> float:
    """
    Compute final trend score on a 0–100 scale.

    Parameters
    ----------
    purchase_intent_score : float
        Average purchase-intent score across product comments (0.0–1.0).
    trend_growth : float
        Normalised trend growth rate (0.0–1.0).
    comment_volume : int
        Total number of comments collected for the product.
    profit_margin : float
        Estimated profit margin (0.0–1.0).
    competition_level : float
        Market competition (0.0–1.0). Higher = more competition = lower score.

    Returns
    -------
    float
        Final score clamped to [0, 100], rounded to 2 decimal places.
    """
    # Normalise inputs to [0, 1]
    intent = max(0.0, min(1.0, purchase_intent_score))
    growth = max(0.0, min(1.0, trend_growth))
    volume_norm = min(comment_volume / COMMENT_VOLUME_CAP, 1.0)
    margin = max(0.0, min(1.0, profit_margin))
    competition = max(0.0, min(1.0, competition_level))

    raw_score = (
        WEIGHT_PURCHASE_INTENT * intent * 100
        + WEIGHT_TREND_GROWTH * growth * 100
        + WEIGHT_COMMENT_VOLUME * volume_norm * 100
        + WEIGHT_PROFIT_MARGIN * margin * 100
        + WEIGHT_COMPETITION * (1.0 - competition) * 100
    )

    final_score = round(max(0.0, min(100.0, raw_score)), 2)

    logger.debug(
        "Trend score: intent=%.2f growth=%.2f vol=%d margin=%.2f comp=%.2f → %.2f",
        intent, growth, comment_volume, margin, competition, final_score,
    )
    return final_score


def score_description(score: float) -> str:
    """Return a human-readable tier label for a given score."""
    if score >= 80:
        return "Winning"
    if score >= 60:
        return "Promising"
    if score >= 40:
        return "Watchlist"
    return "Avoid"

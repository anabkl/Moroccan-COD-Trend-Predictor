"""
SoukAI Recommendation Service
Classifies products into tiers based on their final trend score.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------

TIERS = [
    (80.0, 100.0, "Winning Product", "🏆"),
    (60.0, 79.99, "Promising Product", "⭐"),
    (40.0, 59.99, "Watchlist", "👀"),
    (0.0,  39.99, "Avoid", "❌"),
]


def classify_product(trend_score: float) -> str:
    """
    Return the recommendation label (with emoji) for a given trend score.

    Parameters
    ----------
    trend_score : float
        Final trend score in the range [0, 100].

    Returns
    -------
    str
        One of: "Winning Product 🏆", "Promising Product ⭐", "Watchlist 👀", "Avoid ❌"
    """
    score = max(0.0, min(100.0, trend_score))
    for lower, upper, label, emoji in TIERS:
        if lower <= score <= upper:
            full_label = f"{label} {emoji}"
            logger.debug("Classified score=%.2f → %s", score, full_label)
            return full_label
    return f"Avoid ❌"


def get_tier_counts(products) -> dict:
    """
    Given an iterable of product ORM objects, return a dict with counts per tier.
    Expected keys: winning, promising, watchlist, avoid.
    """
    counts = {"winning": 0, "promising": 0, "watchlist": 0, "avoid": 0}
    for product in products:
        score = product.trend_score or 0.0
        if score >= 80:
            counts["winning"] += 1
        elif score >= 60:
            counts["promising"] += 1
        elif score >= 40:
            counts["watchlist"] += 1
        else:
            counts["avoid"] += 1
    return counts

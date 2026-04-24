"""
SoukAI Explanation Service
Generates human-readable, explainable AI summaries for product recommendations.
"""

from __future__ import annotations

import logging
from typing import List

from app.models import Comment, Product
from app.schemas import ProductExplanation

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Narrative templates
# ---------------------------------------------------------------------------

def _trend_reason(trend_growth: float) -> str:
    if trend_growth >= 0.75:
        return (
            "This product is experiencing explosive growth in Moroccan social media "
            "and COD marketplaces — demand is surging rapidly."
        )
    if trend_growth >= 0.50:
        return (
            "Trend data shows strong upward momentum. Interest in this product has "
            "been climbing steadily over the past weeks."
        )
    if trend_growth >= 0.25:
        return (
            "Moderate trend growth detected. The product is gaining visibility but "
            "has not yet reached peak demand."
        )
    return (
        "Trend growth is currently low. The product may be in an early or declining "
        "phase — monitor closely before investing heavily."
    )


def _competition_reason(competition_level: float) -> str:
    if competition_level <= 0.2:
        return (
            "Market competition is very low — this is a blue-ocean opportunity with "
            "minimal rival sellers in the Moroccan COD space."
        )
    if competition_level <= 0.4:
        return (
            "Low-to-moderate competition. A few sellers are active, but there is "
            "still significant room to capture market share."
        )
    if competition_level <= 0.6:
        return (
            "Moderate competition. The market is somewhat crowded; differentiation "
            "through pricing or packaging is recommended."
        )
    if competition_level <= 0.8:
        return (
            "High competition detected. Many sellers are already promoting this "
            "product. Strong branding and unique angles are critical."
        )
    return (
        "Very high competition. The market is saturated — consider niche "
        "targeting or sourcing a superior variant."
    )


def _profit_reason(profit_margin: float) -> str:
    if profit_margin >= 0.6:
        return (
            "Excellent profit margins — product cost vs. COD selling price offers "
            "an outstanding return on investment."
        )
    if profit_margin >= 0.4:
        return (
            "Good profit margins. After COD fees and returns, the product should "
            "generate solid per-order profit."
        )
    if profit_margin >= 0.2:
        return (
            "Moderate margins. Profitability is acceptable but could be improved "
            "by negotiating better supplier pricing or reducing return rates."
        )
    return (
        "Thin margins detected. Carefully calculate COD return rates and delivery "
        "costs before scaling spend on this product."
    )


def _why_recommended(
    recommendation: str,
    purchase_intent_score: float,
    trend_growth: float,
    competition_level: float,
    profit_margin: float,
) -> str:
    rec_lower = recommendation.lower()

    if "winning" in rec_lower:
        return (
            f"This product scores exceptionally well across all dimensions: "
            f"purchase intent ({purchase_intent_score:.0%}), trend growth "
            f"({trend_growth:.0%}), and profit margin ({profit_margin:.0%}). "
            "It is a top-tier COD opportunity right now."
        )
    if "promising" in rec_lower:
        strengths = []
        if purchase_intent_score >= 0.5:
            strengths.append(f"high buyer interest ({purchase_intent_score:.0%})")
        if trend_growth >= 0.4:
            strengths.append(f"positive trend growth ({trend_growth:.0%})")
        if profit_margin >= 0.35:
            strengths.append(f"healthy margins ({profit_margin:.0%})")
        strength_str = ", ".join(strengths) if strengths else "solid overall metrics"
        return (
            f"Strong potential driven by {strength_str}. "
            "A few areas could still be optimised before scaling."
        )
    if "watchlist" in rec_lower:
        return (
            "This product shows some signals worth watching, but key metrics "
            "(intent, growth, or margins) are not yet strong enough to recommend "
            "immediate scaling. Re-evaluate in 1–2 weeks."
        )
    return (
        "Current metrics do not support a COD investment at this time. "
        "Purchase intent is low, growth is flat, or margins are too thin. "
        "Consider pivoting to a higher-potential product."
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_explanation(
    product: Product,
    top_comments: List[Comment],
) -> ProductExplanation:
    """
    Build a ProductExplanation for the given product ORM instance.

    Parameters
    ----------
    product : Product
        The ORM product object (must have scores populated).
    top_comments : list[Comment]
        Up to 3 highest-intent comments to surface in the explanation.
    """
    recommendation = product.recommendation or "Unknown"
    score = product.trend_score or 0.0
    intent = product.purchase_intent_score or 0.0
    growth = product.trend_growth or 0.0
    competition = product.competition_level or 0.5
    margin = product.estimated_profit_margin or 0.0

    comment_texts = [c.text for c in top_comments[:3]]

    explanation = ProductExplanation(
        product_id=product.id,
        recommendation=recommendation,
        score=score,
        why_recommended=_why_recommended(recommendation, intent, growth, competition, margin),
        top_comments=comment_texts,
        trend_reason=_trend_reason(growth),
        competition_reason=_competition_reason(competition),
        profit_reason=_profit_reason(margin),
    )

    logger.debug("Explanation generated for product_id=%d", product.id)
    return explanation

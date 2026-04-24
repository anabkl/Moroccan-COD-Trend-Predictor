"""
SoukAI Dashboard Router
Aggregated statistics endpoint for the analytics dashboard.
"""

from __future__ import annotations

import logging
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product
from app.schemas import DashboardStats

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Dashboard"])


@router.get(
    "/dashboard-stats",
    response_model=DashboardStats,
    summary="Aggregated dashboard statistics",
)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Return high-level statistics for the SoukAI dashboard:
    - Product tier counts (winning / promising / watchlist / avoid)
    - Average trend score
    - Top categories by product count
    """
    products = db.query(Product).all()

    total = len(products)
    winning = sum(1 for p in products if (p.trend_score or 0) >= 80)
    promising = sum(1 for p in products if 60 <= (p.trend_score or 0) < 80)
    watchlist = sum(1 for p in products if 40 <= (p.trend_score or 0) < 60)
    avoid = sum(1 for p in products if (p.trend_score or 0) < 40)

    avg_score = (
        round(sum(p.trend_score or 0 for p in products) / total, 2) if total else 0.0
    )

    category_counts = Counter(p.category for p in products if p.category)
    top_categories = dict(category_counts.most_common(10))

    logger.debug("Dashboard stats: total=%d winning=%d avg=%.2f", total, winning, avg_score)

    return DashboardStats(
        total_products=total,
        winning_products=winning,
        promising_products=promising,
        watchlist_products=watchlist,
        avoid_products=avoid,
        avg_trend_score=avg_score,
        top_categories=top_categories,
    )

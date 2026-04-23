"""
SoukAI Products Router
Endpoints for listing, filtering, and retrieving individual products.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Comment, Product
from app.schemas import (
    PaginatedProductResponse,
    ProductDetailResponse,
    ProductExplanation,
    ProductResponse,
)
from app.services.explanation_service import generate_explanation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["Products"])


# ---------------------------------------------------------------------------
# GET /products
# ---------------------------------------------------------------------------

@router.get("", response_model=PaginatedProductResponse, summary="List all products")
async def list_products(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of products, optionally filtered by category."""
    query = db.query(Product)

    if category:
        query = query.filter(func.lower(Product.category) == category.lower())

    total = query.count()
    products = (
        query.order_by(Product.trend_score.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return PaginatedProductResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=products,
    )


# ---------------------------------------------------------------------------
# GET /products/top
# ---------------------------------------------------------------------------

@router.get("/top", response_model=List[ProductResponse], summary="Top N products by trend score")
async def top_products(
    n: int = Query(default=10, ge=1, le=50, description="Number of top products"),
    category: Optional[str] = Query(default=None, description="Optional category filter"),
    db: Session = Depends(get_db),
):
    """Return the top N products sorted by trend_score descending."""
    query = db.query(Product)
    if category:
        query = query.filter(func.lower(Product.category) == category.lower())

    products = query.order_by(Product.trend_score.desc()).limit(n).all()
    return products


# ---------------------------------------------------------------------------
# GET /products/{product_id}
# ---------------------------------------------------------------------------

@router.get(
    "/{product_id}",
    response_model=ProductDetailResponse,
    summary="Get product detail with AI explanation",
)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Return a single product including its AI explanation and top comments."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found.")

    # Retrieve top 3 comments by intent score
    top_comments: List[Comment] = (
        db.query(Comment)
        .filter(Comment.product_id == product_id)
        .order_by(Comment.intent_score.desc())
        .limit(3)
        .all()
    )

    explanation: ProductExplanation = generate_explanation(product, top_comments)

    # Build the extended response
    all_comments = (
        db.query(Comment)
        .filter(Comment.product_id == product_id)
        .order_by(Comment.created_at.desc())
        .limit(20)
        .all()
    )

    return ProductDetailResponse(
        **{c: getattr(product, c) for c in ProductResponse.model_fields},
        explanation=explanation,
        comments=all_comments,
    )

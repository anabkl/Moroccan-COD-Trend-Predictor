"""
SoukAI Pydantic Schemas
Request / response models for all API endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Comment schemas
# ---------------------------------------------------------------------------

class CommentBase(BaseModel):
    text: str = Field(..., min_length=1, description="Comment text (Darija/Arabic/French)")
    language: Optional[str] = Field(None, description="Detected language: ar/fr/darija/mixed")


class CommentCreate(CommentBase):
    product_id: int


class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    intent_score: float
    created_at: datetime


# ---------------------------------------------------------------------------
# Product schemas
# ---------------------------------------------------------------------------

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    trend_growth: float = Field(default=0.0, ge=0.0, le=1.0)
    competition_level: float = Field(default=0.5, ge=0.0, le=1.0)
    estimated_profit_margin: float = Field(default=0.0, ge=0.0, le=1.0)


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trend_score: float
    purchase_intent_score: float
    comment_volume: int
    trend_growth: float
    competition_level: float
    estimated_profit_margin: float
    recommendation: Optional[str]
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Analysis schemas
# ---------------------------------------------------------------------------

class AnalyzeCommentRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Comment text to analyze")


class AnalyzeCommentResponse(BaseModel):
    text: str
    intent_score: float = Field(..., ge=0.0, le=1.0)
    detected_language: str
    intent_keywords: List[str]
    purchase_intent_level: str = Field(
        ..., description="high / medium / low"
    )


# ---------------------------------------------------------------------------
# Dashboard schemas
# ---------------------------------------------------------------------------

class DashboardStats(BaseModel):
    total_products: int
    winning_products: int
    promising_products: int
    watchlist_products: int
    avoid_products: int
    avg_trend_score: float
    top_categories: Dict[str, int] = Field(
        default_factory=dict,
        description="Category name → product count mapping",
    )


# ---------------------------------------------------------------------------
# Explanation schemas
# ---------------------------------------------------------------------------

class ProductExplanation(BaseModel):
    product_id: int
    recommendation: str
    score: float
    why_recommended: str
    top_comments: List[str] = Field(default_factory=list)
    trend_reason: str
    competition_reason: str
    profit_reason: str


class ProductDetailResponse(ProductResponse):
    """Extended product response that includes AI explanation."""
    explanation: Optional[ProductExplanation] = None
    comments: List[CommentResponse] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# CSV upload schema
# ---------------------------------------------------------------------------

class CSVUploadResponse(BaseModel):
    message: str
    products_imported: int = 0
    comments_imported: int = 0
    errors: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Generic response wrappers
# ---------------------------------------------------------------------------

class PaginatedProductResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[ProductResponse]

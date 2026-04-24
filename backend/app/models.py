"""
SoukAI ORM Models
Defines Product and Comment tables compatible with SQLite and PostgreSQL.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    image_url = Column(String(500), nullable=True)

    # Computed scores (populated by scoring_service)
    trend_score = Column(Float, default=0.0, nullable=False)
    purchase_intent_score = Column(Float, default=0.0, nullable=False)
    comment_volume = Column(Integer, default=0, nullable=False)
    trend_growth = Column(Float, default=0.0, nullable=False)       # 0.0–1.0
    competition_level = Column(Float, default=0.5, nullable=False)  # 0.0–1.0
    estimated_profit_margin = Column(Float, default=0.0, nullable=False)  # 0.0–1.0

    # Classification result
    recommendation = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
    )

    # Relationships
    comments = relationship(
        "Comment",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name!r} score={self.trend_score}>"


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text = Column(Text, nullable=False)
    language = Column(String(20), nullable=True)   # ar / fr / darija / mixed
    intent_score = Column(Float, default=0.0, nullable=False)  # 0.0–1.0
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment id={self.id} product_id={self.product_id} lang={self.language}>"

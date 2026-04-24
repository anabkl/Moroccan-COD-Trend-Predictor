"""
SoukAI Data Service
Handles CSV ingestion, text cleaning, score computation, and DB seeding.
"""

from __future__ import annotations

import logging
from typing import List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models import Comment, Product
from app.services.nlp_service import analyze_intent, compute_avg_intent_score
from app.services.recommendation_service import classify_product
from app.services.scoring_service import compute_trend_score
from app.utils.text_utils import clean_text, detect_language

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CSV ingestion
# ---------------------------------------------------------------------------

def load_products_from_csv(file_path: str, db: Session) -> dict:
    """
    Parse a products CSV, compute scores, and persist to DB.

    Expected columns (flexible – missing optional columns use defaults):
        name, category, description, price, image_url,
        trend_growth, competition_level, estimated_profit_margin
    """
    errors: List[str] = []
    imported = 0

    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except Exception as exc:
        return {"products_imported": 0, "errors": [f"CSV read error: {exc}"]}

    # Normalise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    required = {"name", "category"}
    missing = required - set(df.columns)
    if missing:
        return {
            "products_imported": 0,
            "errors": [f"Missing required columns: {missing}"],
        }

    for idx, row in df.iterrows():
        try:
            name = str(row.get("name", "")).strip()
            category = str(row.get("category", "")).strip()
            if not name or not category:
                errors.append(f"Row {idx}: name/category empty – skipped.")
                continue

            description = clean_text(str(row.get("description", "") or ""))
            price = _safe_float(row.get("price"))
            image_url = str(row.get("image_url", "") or "")

            trend_growth = _safe_float(row.get("trend_growth"), default=0.5, lo=0.0, hi=1.0)
            competition = _safe_float(row.get("competition_level"), default=0.5, lo=0.0, hi=1.0)
            margin = _safe_float(row.get("estimated_profit_margin"), default=0.3, lo=0.0, hi=1.0)

            # Intent score will be recalculated when comments arrive; use 0.5 as placeholder
            intent = _safe_float(row.get("purchase_intent_score"), default=0.5, lo=0.0, hi=1.0)
            comment_volume = int(row.get("comment_volume", 0) or 0)

            trend_score = compute_trend_score(intent, trend_growth, comment_volume, margin, competition)
            recommendation = classify_product(trend_score)

            product = Product(
                name=name,
                category=category,
                description=description,
                price=price,
                image_url=image_url or None,
                trend_score=trend_score,
                purchase_intent_score=intent,
                comment_volume=comment_volume,
                trend_growth=trend_growth,
                competition_level=competition,
                estimated_profit_margin=margin,
                recommendation=recommendation,
            )
            db.add(product)
            imported += 1
        except Exception as exc:
            errors.append(f"Row {idx}: {exc}")

    db.commit()
    logger.info("CSV import complete: %d products, %d errors", imported, len(errors))
    return {"products_imported": imported, "errors": errors}


def load_comments_from_csv(file_path: str, db: Session) -> dict:
    """
    Parse a comments CSV, detect intent, and persist to DB.

    Expected columns: product_id, text
    Optional columns: language
    """
    errors: List[str] = []
    imported = 0

    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except Exception as exc:
        return {"comments_imported": 0, "errors": [f"CSV read error: {exc}"]}

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    for idx, row in df.iterrows():
        try:
            product_id = int(row.get("product_id", 0) or 0)
            text = str(row.get("text", "") or "").strip()
            if not product_id or not text:
                errors.append(f"Row {idx}: product_id/text missing – skipped.")
                continue

            product = db.get(Product, product_id)
            if not product:
                errors.append(f"Row {idx}: product_id={product_id} not found – skipped.")
                continue

            cleaned = clean_text(text)
            analysis = analyze_intent(cleaned)

            comment = Comment(
                product_id=product_id,
                text=text,
                language=analysis["detected_language"],
                intent_score=analysis["intent_score"],
            )
            db.add(comment)
            imported += 1

            # Update the parent product's intent score and volume
            _refresh_product_scores(product, db, commit=False)

        except Exception as exc:
            errors.append(f"Row {idx}: {exc}")

    db.commit()
    logger.info("Comment CSV import complete: %d comments, %d errors", imported, len(errors))
    return {"comments_imported": imported, "errors": errors}


# ---------------------------------------------------------------------------
# Score refresh helper
# ---------------------------------------------------------------------------

def _refresh_product_scores(product: Product, db: Session, commit: bool = True) -> None:
    """Recompute intent score and trend score from current comments."""
    comment_texts = [c.text for c in product.comments]
    avg_intent = compute_avg_intent_score(comment_texts) if comment_texts else product.purchase_intent_score

    product.purchase_intent_score = avg_intent
    product.comment_volume = len(comment_texts)
    product.trend_score = compute_trend_score(
        avg_intent,
        product.trend_growth,
        product.comment_volume,
        product.estimated_profit_margin,
        product.competition_level,
    )
    product.recommendation = classify_product(product.trend_score)

    if commit:
        db.commit()
        db.refresh(product)


# ---------------------------------------------------------------------------
# Sample seed data
# ---------------------------------------------------------------------------

SAMPLE_PRODUCTS = [
    {
        "name": "Ceinture Minceur Chauffante",
        "category": "Santé & Beauté",
        "description": "Ceinture chauffante pour affiner la taille – idéale pour les femmes actives.",
        "price": 149.0,
        "trend_growth": 0.82,
        "competition_level": 0.35,
        "estimated_profit_margin": 0.62,
        "comments": [
            "bchhal had ceinture? kifach ncommandi 3afak",
            "wach katwsl l dar? livraison combien?",
            "prix dyal had l'article? 3afak wach kayen f stock?",
            "زوين بزاف! بشحال واش كاين؟",
            "thaman chhal hadi? bghit nchri wahed",
            "wach momkin ndir commande? fin kayen?",
            "superbe produit! comment commander?",
            "nice product tbark allah, wach ghali?",
        ],
    },
    {
        "name": "Lampe LED Anti-Moustiques",
        "category": "Maison & Jardin",
        "description": "Piège à moustiques UV rechargeable, silencieux, sans produits chimiques.",
        "price": 89.0,
        "trend_growth": 0.70,
        "competition_level": 0.40,
        "estimated_profit_margin": 0.55,
        "comments": [
            "wach katwsl l Casablanca? bchhal had lampe?",
            "kifach ncommandi? 3afak wach kayen?",
            "commande possible? livraison rapide?",
            "bghit nchri wahed, thaman chhal?",
            "واش كاين فالمغرب؟ كيفاش نطلب؟",
            "zwin had lampe, prix?",
            "nice, available? how to order?",
        ],
    },
    {
        "name": "Masseur Électrique Cervical",
        "category": "Santé & Beauté",
        "description": "Masseur cervical EMS avec chaleur infrarouge pour soulager les douleurs.",
        "price": 199.0,
        "trend_growth": 0.78,
        "competition_level": 0.30,
        "estimated_profit_margin": 0.58,
        "comments": [
            "bchhal had masseur? kifach ncommandi?",
            "wach khadama mzyan? 3afak prix?",
            "livraison Maroc? commande possible?",
            "بشحال وكيفاش نطلب؟",
            "chri had had, bghit wahed!",
            "comment commander? disponible?",
        ],
    },
    {
        "name": "Brosse Nettoyante Visage Électrique",
        "category": "Santé & Beauté",
        "description": "Brosse rotative rechargeable pour un nettoyage en profondeur.",
        "price": 120.0,
        "trend_growth": 0.65,
        "competition_level": 0.50,
        "estimated_profit_margin": 0.50,
        "comments": [
            "wach ghali? kifach ncommandi 3afak",
            "prix? disponible au Maroc?",
            "bghit nchri, bchhal?",
            "tbarklah zwina, thaman?",
            "واش كاين؟ بشحال؟",
        ],
    },
    {
        "name": "Support Voiture Téléphone Magnétique",
        "category": "Auto & Moto",
        "description": "Support magnétique universel pour tableau de bord, rotation 360°.",
        "price": 59.0,
        "trend_growth": 0.55,
        "competition_level": 0.65,
        "estimated_profit_margin": 0.48,
        "comments": [
            "bchhal? wach katwsl?",
            "prix livraison?",
            "nice product, how to order?",
            "kifach ndir commande?",
        ],
    },
    {
        "name": "Gants de Ménage Imperméables",
        "category": "Maison & Jardin",
        "description": "Gants multifonctions imperméables pour cuisine et nettoyage.",
        "price": 45.0,
        "trend_growth": 0.42,
        "competition_level": 0.72,
        "estimated_profit_margin": 0.38,
        "comments": [
            "bchhal had pair?",
            "zwina, thaman chhal?",
            "disponible?",
        ],
    },
    {
        "name": "Organisateur Câbles Bureau",
        "category": "Électronique",
        "description": "Boîtier organisateur de câbles en cuir PU pour bureau propre.",
        "price": 75.0,
        "trend_growth": 0.38,
        "competition_level": 0.60,
        "estimated_profit_margin": 0.42,
        "comments": [
            "zwin, prix?",
            "bchhal? wach kayen?",
            "magnifique! disponible?",
        ],
    },
    {
        "name": "Semelles Chauffantes Connectées",
        "category": "Mode & Vêtements",
        "description": "Semelles thermorégulées via application smartphone, batterie lithium.",
        "price": 249.0,
        "trend_growth": 0.90,
        "competition_level": 0.20,
        "estimated_profit_margin": 0.70,
        "comments": [
            "bchhal had semelles? 3afak ncommandi",
            "wach katwsl? livraison express?",
            "kifach ncommandi? bghit wahed!",
            "prix? disponible Maroc? wach ghali?",
            "واش كاين؟ كيفاش نطلب؟ بشحال؟",
            "thaman chhal? wach khadama mzyan?",
            "superbe! combien? comment commander?",
            "3afak bchhal wach momkin nchri?",
        ],
    },
    {
        "name": "Presse-Agrumes Automatique USB",
        "category": "Cuisine",
        "description": "Extracteur de jus portable rechargeable par USB, 380 ml.",
        "price": 110.0,
        "trend_growth": 0.60,
        "competition_level": 0.45,
        "estimated_profit_margin": 0.52,
        "comments": [
            "bchhal? kifach ncommandi?",
            "wach katwsl l Marrakech?",
            "prix livraison combien?",
            "واش كاين فستوك؟",
            "nice product, available?",
        ],
    },
    {
        "name": "Sac à Dos Imperméable Anti-Vol",
        "category": "Mode & Vêtements",
        "description": "Sac à dos étanche avec port USB intégré et fermeture anti-vol.",
        "price": 185.0,
        "trend_growth": 0.68,
        "competition_level": 0.42,
        "estimated_profit_margin": 0.56,
        "comments": [
            "bchhal had sac? kifach ncommandi 3afak?",
            "prix et livraison?",
            "bghit wahed, wach kayen l Fes?",
            "tbarklah zwin, thaman?",
            "واش كاين؟ بشحال؟",
            "disponible? comment commander?",
        ],
    },
]


def seed_sample_data(db: Session) -> None:
    """Seed the database with sample products and comments if the DB is empty."""
    if db.query(Product).count() > 0:
        logger.info("Database already has products – skipping seed.")
        return

    logger.info("Seeding sample data (%d products)…", len(SAMPLE_PRODUCTS))

    for item in SAMPLE_PRODUCTS:
        comment_texts: List[str] = item.pop("comments", [])

        trend_growth = item.pop("trend_growth", 0.5)
        competition_level = item.pop("competition_level", 0.5)
        estimated_profit_margin = item.pop("estimated_profit_margin", 0.3)

        # Bootstrap intent from comments
        avg_intent = compute_avg_intent_score(comment_texts) if comment_texts else 0.5
        comment_volume = len(comment_texts)

        trend_score = compute_trend_score(
            avg_intent, trend_growth, comment_volume, estimated_profit_margin, competition_level
        )
        recommendation = classify_product(trend_score)

        product = Product(
            **item,
            trend_growth=trend_growth,
            competition_level=competition_level,
            estimated_profit_margin=estimated_profit_margin,
            purchase_intent_score=avg_intent,
            comment_volume=comment_volume,
            trend_score=trend_score,
            recommendation=recommendation,
        )
        db.add(product)
        db.flush()  # get product.id

        for text in comment_texts:
            cleaned = clean_text(text)
            analysis = analyze_intent(cleaned)
            comment = Comment(
                product_id=product.id,
                text=text,
                language=analysis["detected_language"],
                intent_score=analysis["intent_score"],
            )
            db.add(comment)

    db.commit()
    logger.info("Sample data seeded successfully.")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _safe_float(
    value,
    default: float = 0.0,
    lo: Optional[float] = None,
    hi: Optional[float] = None,
) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError):
        f = default
    if lo is not None:
        f = max(lo, f)
    if hi is not None:
        f = min(hi, f)
    return f

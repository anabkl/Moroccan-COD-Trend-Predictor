"""
SoukAI Analysis Router
Endpoints for single-comment intent analysis and CSV bulk upload.
"""

from __future__ import annotations

import io
import logging
import tempfile
import os

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    AnalyzeCommentRequest,
    AnalyzeCommentResponse,
    CSVUploadResponse,
)
from app.services.data_service import load_comments_from_csv, load_products_from_csv
from app.services.nlp_service import analyze_intent
from app.utils.text_utils import clean_text

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Analysis"])


# ---------------------------------------------------------------------------
# POST /analyze-comment
# ---------------------------------------------------------------------------

@router.post(
    "/analyze-comment",
    response_model=AnalyzeCommentResponse,
    summary="Analyse a single comment for purchase intent",
)
async def analyze_comment(request: AnalyzeCommentRequest):
    """
    Analyse a Darija / Arabic / French comment and return:
    - intent_score (0.0–1.0)
    - detected_language
    - matched intent keywords
    - purchase_intent_level (high / medium / low)
    """
    if not request.text.strip():
        raise HTTPException(status_code=422, detail="Comment text cannot be empty.")

    cleaned = clean_text(request.text)
    result = analyze_intent(cleaned)

    return AnalyzeCommentResponse(
        text=request.text,
        intent_score=result["intent_score"],
        detected_language=result["detected_language"],
        intent_keywords=result["intent_keywords"],
        purchase_intent_level=result["purchase_intent_level"],
    )


# ---------------------------------------------------------------------------
# POST /upload-csv
# ---------------------------------------------------------------------------

@router.post(
    "/upload-csv",
    response_model=CSVUploadResponse,
    summary="Upload a CSV file of products or comments",
)
async def upload_csv(
    file: UploadFile = File(..., description="CSV file (products or comments)"),
    csv_type: str = "products",
    db: Session = Depends(get_db),
):
    """
    Upload a CSV file and import it into the database.

    - **csv_type=products** – expects columns: name, category, [description, price, ...]
    - **csv_type=comments** – expects columns: product_id, text
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    if csv_type not in ("products", "comments"):
        raise HTTPException(
            status_code=400,
            detail="csv_type must be 'products' or 'comments'.",
        )

    # Read uploaded bytes
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Write to a temporary file in the current working directory to avoid /tmp
    tmp_path = f"_upload_{file.filename}"
    try:
        async with aiofiles.open(tmp_path, "wb") as f_out:
            await f_out.write(contents)

        if csv_type == "products":
            result = load_products_from_csv(tmp_path, db)
            return CSVUploadResponse(
                message=f"Products import complete.",
                products_imported=result.get("products_imported", 0),
                errors=result.get("errors", []),
            )
        else:
            result = load_comments_from_csv(tmp_path, db)
            return CSVUploadResponse(
                message="Comments import complete.",
                comments_imported=result.get("comments_imported", 0),
                errors=result.get("errors", []),
            )
    except Exception as exc:
        logger.exception("CSV upload failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Import failed: {exc}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

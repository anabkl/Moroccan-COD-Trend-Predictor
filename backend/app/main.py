"""
SoukAI – FastAPI Application Entry Point
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import create_tables, SessionLocal
from app.routers import analysis, dashboard, products
from app.services.data_service import seed_sample_data

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "SoukAI Team",
        "url": "https://github.com/anabkl/Moroccan-COD-Trend-Predictor",
    },
    license_info={
        "name": "MIT",
    },
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Startup / shutdown lifecycle
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Starting %s v%s …", settings.PROJECT_NAME, settings.API_VERSION)
    create_tables()

    db = SessionLocal()
    try:
        seed_sample_data(db)
    finally:
        db.close()

    logger.info("Startup complete. Docs at /docs")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("%s shutting down.", settings.PROJECT_NAME)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"], summary="Health check")
async def health_check():
    """Returns 200 OK when the service is up and the DB is reachable."""
    from app.database import engine
    from sqlalchemy import text

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:  # pragma: no cover
        logger.error("DB health check failed: %s", exc)
        db_status = "error"

    return JSONResponse(
        content={
            "status": "ok" if db_status == "ok" else "degraded",
            "version": settings.API_VERSION,
            "project": settings.PROJECT_NAME,
            "database": db_status,
        }
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(products.router)
app.include_router(analysis.router)
app.include_router(dashboard.router)

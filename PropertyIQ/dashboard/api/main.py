"""
PropertyIQ FastAPI Backend — Main Entry Point

This is the entry point of the entire API. It boots the application, loads models
into memory, registers all routes, and serves the health endpoint.

When this file runs clean and localhost:8000/docs opens with all routes visible,
Phase 1 backend foundation is done.
"""

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import startup, model_store, encoding_store, OUTPUTS_DIR
from models.schemas import HealthResponse


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING SETUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

logger = logging.getLogger("propertyiq.main")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LIFESPAN — STARTUP AND SHUTDOWN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Replaces deprecated @app.on_event("startup") and @app.on_event("shutdown").
    """
    # ── STARTUP ──────────────────────────────────────────
    logger.info("FastAPI lifespan startup triggered")
    startup()  # loads models + encodings + verifies files
    yield
    # ── SHUTDOWN ─────────────────────────────────────────
    logger.info("PropertyIQ API shutting down")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FASTAPI APP INSTANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="PropertyIQ API",
    description="""
## PropertyIQ — Property Valuation & Drift Detection Platform

B2B SaaS API for Indian bank credit officers and risk analysts.

### What this API does
- **Live property valuation** using a Random Forest model trained on 600,000 Indian properties
- **Drift detection** — KS-test results across 14 features and 10 cities
- **SHAP explainability** — feature importance and per-prediction drivers
- **Price forecasting** — implied CAGR from 2020→2025 actual data for 10 cities
- **Trust translation** — converts model confidence into TRUSTED / CAUTION / FIELD VERIFICATION

### Data
- Training data: 300,000 properties (2020)
- Drift window: 300,000 properties (2025)
- Model MAPE: 1.61% (sale), 19.64% (rental)
- All outputs pre-computed — this API is a serving layer over notebook outputs

### RBI Alignment
Built in alignment with RBI Model Risk Management Circular, 2023.
    """,
    version="1.0.0",
    contact={
        "name": "PropertyIQ — DSBDA Capstone 2026",
    },
    license_info={
        "name": "DSBDA CA 2026 — Component 1",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CORS MIDDLEWARE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:5174",    # ← add this
        "http://localhost:3000",   # fallback
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",    # ← add this
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IMPORT AND REGISTER ALL ROUTERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from routes.drift import router as drift_router
from routes.forecast import router as forecast_router
from routes.model import router as model_router
from routes.shap import router as shap_router
from routes.predict import router as predict_router

app.include_router(
    drift_router,
    prefix="/api/drift",
    tags=["Drift Detection"],
)
app.include_router(
    forecast_router,
    prefix="/api/forecast",
    tags=["Price Forecast"],
)
app.include_router(
    model_router,
    prefix="/api/model",
    tags=["Model Registry"],
)
app.include_router(
    shap_router,
    prefix="/api/shap",
    tags=["SHAP Explainability"],
)
app.include_router(
    predict_router,
    prefix="/api/predict",
    tags=["Valuation Engine"],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROOT ENDPOINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get(
    "/",
    tags=["System"],
    summary="API root — confirms service is running"
)
async def root():
    """
    Root endpoint that provides API overview and navigation.
    """
    return {
        "service":     "PropertyIQ API",
        "version":     "1.0.0",
        "status":      "running",
        "docs":        "/docs",
        "description": "Property Valuation & Drift Detection Platform",
        "endpoints": {
            "predict":  "/api/predict/valuation",
            "drift":    "/api/drift/summary",
            "forecast": "/api/forecast/all",
            "model":    "/api/model/registry",
            "shap":     "/api/shap/importance",
            "health":   "/health",
        }
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEALTH ENDPOINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check — confirms models loaded and outputs present"
)
async def health():
    """
    Health check endpoint that verifies:
    - Models are loaded into memory
    - Encodings are loaded
    - All required output JSON files exist
    
    Returns:
        HealthResponse with status, models_loaded, encodings_loaded, outputs_verified, version
    """
    required = [
        "inspection_report.json",
        "preprocessing_report.json",
        "feature_report.json",
        "encodings.json",
        "model_registry.json",
        "ks_results.json",
        "drift_results.json",
        "rolling_mape.json",
        "chi2_results.json",
        "shap_values.json",
        "forecast_params.json",
    ]
    
    outputs_verified = sum(
        1 for f in required
        if (OUTPUTS_DIR / f).exists()
    )
    
    return HealthResponse(
        status           = "healthy" if model_store.is_loaded() else "degraded",
        models_loaded    = model_store.is_loaded(),
        encodings_loaded = encoding_store.is_loaded(),
        outputs_verified = outputs_verified,
        version          = "1.0.0",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GLOBAL EXCEPTION HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Catch-all exception handler for unhandled errors.
    Logs the error and returns a 500 response with error details.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error":   "Internal server error",
            "detail":  str(exc),
            "path":    str(request.url),
        }
    )

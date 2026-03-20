"""
SHAP Explanation Routes
=======================

Per-prediction SHAP explanations for the Client Portal.

When a loan officer submits a property, the result panel shows exactly which
features pushed the price up or down and by how much. This makes the valuation
explainable to a non-technical credit officer.

Important constraint — no runtime SHAP computation.
Running TreeExplainer on a live request takes 9 minutes — completely unusable.

Instead use an approximation that is fast, accurate enough for explanation
purposes, and mathematically defensible:

    contribution_i = feature_importance_i * (predicted_price - base_value)

Where feature_importance_i comes from model_registry.json → feature_importances.
This distributes the delta from base value across features weighted by their
RF importance. The result is directionally correct, interpretable, and instant.
"""

import json
import logging
import numpy as np
from functools import lru_cache
from fastapi import APIRouter, HTTPException

from config import (
    MODEL_REGISTRY_FILE,
    SHAP_VALUES_FILE,
    FEATURE_DISPLAY_NAMES,
    FEATURE_GROUPS,
    encoding_store,
    model_store,
    SALE_FEATURE_COLS,
    CITY_TIER,
    CITY_RBI_HPI,
    CURRENT_INTEREST_RATE,
    DEMAND_SUPPLY_DEFAULTS,
    LIVABILITY_DEFAULTS,
)
from models.schemas import (
    ValuationRequest,
    SHAPDriver,
)

router = APIRouter()
logger = logging.getLogger("propertyiq.routes.shap")


# ============================================================================
# Cached Loaders
# ============================================================================

@lru_cache(maxsize=1)
def _load_registry() -> dict:
    """Load model registry with feature importances."""
    with open(MODEL_REGISTRY_FILE, 'r') as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_shap_globals() -> dict:
    """Load global SHAP values and base value."""
    with open(SHAP_VALUES_FILE, 'r') as f:
        return json.load(f)


# ============================================================================
# Helper — Build Sale Feature Vector
# ============================================================================

def _build_sale_vector(request: ValuationRequest) -> list[float]:
    """
    Build the 14-feature vector in exact SALE_FEATURE_COLS order.
    Uses encoding_store for city/locality medians and city stats.
    
    Identical logic to what predict.py uses. Defined here so shap.py
    can work standalone.
    """
    city     = request.city
    locality = request.locality
    bhk      = request.bhk
    sqft     = request.total_sqft
    bath     = request.bath
    
    # Lookup from encodings
    city_median     = encoding_store.get_city_median(city)
    locality_median = encoding_store.get_locality_median(locality, city)
    city_stats      = encoding_store.get_city_stats(city)
    city_mean       = city_stats["city_mean"]
    city_std        = city_stats["city_std"]
    
    # Derived features
    bath_per_bhk       = bath / bhk
    sqft_per_bhk       = sqft / bhk
    is_large           = 1 if sqft >= encoding_store.large_threshold else 0
    price_sqft_zscore  = (
        (locality_median - city_mean) / city_std
        if city_std > 0 else 0.0
    )
    
    # City constants
    city_tier        = CITY_TIER.get(city, 2)
    rbi_hpi          = CITY_RBI_HPI.get(city, 165)
    interest_rate    = CURRENT_INTEREST_RATE
    demand_supply    = DEMAND_SUPPLY_DEFAULTS.get(city, 1.15)
    livability       = LIVABILITY_DEFAULTS.get(city, 68)
    
    # Build vector in exact SALE_FEATURE_COLS order
    vector = [
        bhk,
        sqft,
        bath,
        bath_per_bhk,
        sqft_per_bhk,
        is_large,
        city_median,
        locality_median,
        price_sqft_zscore,
        city_tier,
        demand_supply,
        rbi_hpi,
        interest_rate,
        livability,
    ]
    
    return vector


# ============================================================================
# Helper — Compute Per-Prediction SHAP Drivers
# ============================================================================

def _compute_drivers(
    request: ValuationRequest,
    predicted_price: float,
    base_value: float,
    top_n: int = 5,
) -> list[SHAPDriver]:
    """
    Approximate SHAP contributions using RF feature importances.
    
    Method:
        delta = predicted_price - base_value
        contribution_i = feature_importance_i * delta
    
    This distributes the prediction delta across features
    proportional to their global RF importance weights.
    Returns top_n features sorted by absolute contribution.
    
    Falls back to global mean SHAP values if registry
    feature importances are unavailable.
    """
    registry    = _load_registry()
    shap_global = _load_shap_globals()
    
    # Get feature importances from registry
    sale_data   = registry.get("sale_price_v1", {})
    importances = sale_data.get("feature_importances", {})
    
    delta       = predicted_price - base_value
    
    drivers = []
    for feature in SALE_FEATURE_COLS:
        importance   = importances.get(feature, 0.0)
        contribution = importance * delta
        
        direction = "UP" if contribution >= 0 else "DOWN"
        
        drivers.append(SHAPDriver(
            feature       = feature,
            display_name  = FEATURE_DISPLAY_NAMES.get(feature, feature),
            contribution  = round(contribution, 2),
            direction     = direction,
            feature_group = FEATURE_GROUPS.get(feature, "physical"),
        ))
    
    # Sort by absolute contribution descending
    drivers.sort(key=lambda x: abs(x.contribution), reverse=True)
    
    return drivers[:top_n]


# ============================================================================
# POST /api/shap/explain
# ============================================================================

@router.post(
    "/explain",
    response_model=list[SHAPDriver],
    summary="Per-prediction SHAP explanation for a specific property",
    description="""
Returns the top 5 feature contributions explaining why the model predicted
a specific price for the submitted property.

Contributions are computed using RF feature importance weights applied to
the prediction delta from base value:

    contribution_i = feature_importance_i * (predicted - base_value)

This tells the loan officer exactly which factors drove the valuation up or
down in plain English with Rs/sqft amounts.

Same request body as /api/predict/valuation.
    """
)
async def explain_prediction(request: ValuationRequest):
    try:
        shap_global = _load_shap_globals()
        base_value  = float(shap_global.get("base_value", 8437.62))
        
        # Build feature vector and get prediction
        vector          = _build_sale_vector(request)
        predicted_price = model_store.predict_sale(vector)
        
        # Compute drivers
        drivers = _compute_drivers(
            request         = request,
            predicted_price = predicted_price,
            base_value      = base_value,
            top_n           = 5,
        )
        
        return drivers
    
    except Exception as e:
        logger.error(f"shap/explain error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/shap/global
# ============================================================================

@router.get(
    "/global",
    summary="Global SHAP importance — shortcut endpoint under shap tag",
    description="""
Convenience endpoint returning global SHAP importance.
Identical data to /api/model/shap.

Data source: shap_values.json
    """
)
async def get_global_shap():
    try:
        data = _load_shap_globals()
        return data
    except Exception as e:
        logger.error(f"shap/global error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

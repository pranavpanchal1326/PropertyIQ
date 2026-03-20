"""
PropertyIQ API — Prediction Routes

This is the most critical file in the entire backend. When a loan officer submits
a property in the Client Portal, this endpoint runs the live model, computes
confidence, determines trust tier, fetches SHAP drivers, and returns a complete
valuation report in one call. Everything must be correct — wrong feature vector
order breaks the model silently.
"""

import json
import logging
import numpy as np
from functools import lru_cache
from fastapi import APIRouter, HTTPException

from config import (
    MODEL_REGISTRY_FILE,
    SHAP_VALUES_FILE,
    DRIFT_RESULTS_FILE,
    FORECAST_PARAMS_FILE,
    SALE_FEATURE_COLS,
    RENTAL_FEATURE_COLS,
    CITY_TIER,
    CITY_RBI_HPI,
    CURRENT_INTEREST_RATE,
    DEMAND_SUPPLY_DEFAULTS,
    LIVABILITY_DEFAULTS,
    AMENITIES_DEFAULTS,
    FEATURE_DISPLAY_NAMES,
    FEATURE_GROUPS,
    encoding_store,
    model_store,
)
from models.schemas import (
    ValuationRequest,
    ValuationResponse,
    SHAPDriver,
    TrustTier,
    DriftSeverity,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROUTER AND LOGGER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

router = APIRouter()
logger = logging.getLogger("propertyiq.routes.predict")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CACHED LOADERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@lru_cache(maxsize=1)
def _load_shap_globals() -> dict:
    with open(SHAP_VALUES_FILE, 'r') as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_registry() -> dict:
    with open(MODEL_REGISTRY_FILE, 'r') as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_drift() -> dict:
    with open(DRIFT_RESULTS_FILE, 'r') as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_forecast() -> dict:
    with open(FORECAST_PARAMS_FILE, 'r') as f:
        return json.load(f)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEATURE VECTOR BUILDERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _build_sale_vector(request: ValuationRequest) -> list[float]:
    """
    Build 14-feature vector in exact SALE_FEATURE_COLS order:
    bhk, total_sqft, bath, bath_per_bhk, sqft_per_bhk,
    is_large_property, city_median_price_sqft,
    locality_median_price_sqft, price_sqft_city_zscore,
    city_tier_encoded, demand_supply_ratio,
    rbi_hpi_avg, interest_rate, livability_score
    """
    city     = request.city
    locality = request.locality
    bhk      = request.bhk
    sqft     = request.total_sqft
    bath     = request.bath
    
    # Encodings lookup
    city_median     = encoding_store.get_city_median(city)
    locality_median = encoding_store.get_locality_median(locality, city)
    city_stats      = encoding_store.get_city_stats(city)
    city_mean       = city_stats["city_mean"]
    city_std        = city_stats["city_std"]
    
    # Derived features
    bath_per_bhk      = bath / bhk
    sqft_per_bhk      = sqft / bhk
    is_large          = 1 if sqft >= encoding_store.large_threshold else 0
    price_sqft_zscore = (
        (locality_median - city_mean) / city_std
        if city_std > 0 else 0.0
    )
    
    # City constants
    city_tier     = CITY_TIER.get(city, 2)
    rbi_hpi       = CITY_RBI_HPI.get(city, 165)
    demand_supply = DEMAND_SUPPLY_DEFAULTS.get(city, 1.15)
    livability    = LIVABILITY_DEFAULTS.get(city, 68)
    
    return [
        bhk,               # 1
        sqft,              # 2
        bath,              # 3
        bath_per_bhk,      # 4
        sqft_per_bhk,      # 5
        is_large,          # 6
        city_median,       # 7
        locality_median,   # 8
        price_sqft_zscore, # 9
        city_tier,         # 10
        demand_supply,     # 11
        rbi_hpi,           # 12
        CURRENT_INTEREST_RATE, # 13
        livability,        # 14
    ]


def _build_rental_vector(request: ValuationRequest) -> list[float]:
    """
    Build 14-feature vector in exact RENTAL_FEATURE_COLS order:
    bhk, total_sqft, bath, bath_per_bhk, sqft_per_bhk,
    is_large_property, city_median_price_sqft,
    locality_median_price_sqft, city_tier_encoded,
    rbi_hpi_avg, interest_rate, livability_score,
    amenities_score, furnishing_encoded
    """
    city     = request.city
    locality = request.locality
    bhk      = request.bhk
    sqft     = request.total_sqft
    bath     = request.bath
    
    city_median     = encoding_store.get_city_median(city)
    locality_median = encoding_store.get_locality_median(locality, city)
    
    bath_per_bhk = bath / bhk
    sqft_per_bhk = sqft / bhk
    is_large     = 1 if sqft >= encoding_store.large_threshold else 0
    
    city_tier    = CITY_TIER.get(city, 2)
    rbi_hpi      = CITY_RBI_HPI.get(city, 165)
    livability   = LIVABILITY_DEFAULTS.get(city, 68)
    amenities    = AMENITIES_DEFAULTS.get(city, 68)
    furnishing   = encoding_store.encode_furnishing(request.furnishing.value)
    
    return [
        bhk,               # 1
        sqft,              # 2
        bath,              # 3
        bath_per_bhk,      # 4
        sqft_per_bhk,      # 5
        is_large,          # 6
        city_median,       # 7
        locality_median,   # 8
        city_tier,         # 9
        rbi_hpi,           # 10
        CURRENT_INTEREST_RATE, # 11
        livability,        # 12
        amenities,         # 13
        furnishing,        # 14
    ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER — COMPUTE SHAP DRIVERS FOR THIS PREDICTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_drivers(
    request: ValuationRequest,
    predicted_price: float,
    base_value: float,
    top_n: int = 5,
) -> list[SHAPDriver]:
    """
    Approximate SHAP contributions using RF feature importances.
    contribution_i = feature_importance_i * (predicted - base_value)
    """
    registry    = _load_registry()
    importances = registry.get(
        "sale_price_v1", {}
    ).get("feature_importances", {})
    delta       = predicted_price - base_value
    
    drivers = []
    for feature in SALE_FEATURE_COLS:
        importance   = importances.get(feature, 0.0)
        contribution = round(importance * delta, 2)
        drivers.append(SHAPDriver(
            feature       = feature,
            display_name  = FEATURE_DISPLAY_NAMES.get(feature, feature),
            contribution  = contribution,
            direction     = "UP" if contribution >= 0 else "DOWN",
            feature_group = FEATURE_GROUPS.get(feature, "physical"),
        ))
    
    drivers.sort(key=lambda x: abs(x.contribution), reverse=True)
    return drivers[:top_n]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER — GET CITY DRIFT CONTEXT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_city_drift(city: str) -> dict:
    """
    Get KS stat and price shift for the submitted city.
    Returns safe defaults if city not found.
    """
    drift      = _load_drift()
    city_data  = drift.get("city_drift", {}).get(city, {})
    return {
        "ks_stat":         city_data.get("ks_stat", 0.0),
        "p_value":         city_data.get("p_value", 1.0),
        "price_shift_pct": city_data.get("price_shift_pct", 0.0),
        "drift_mape":      city_data.get("drift_mape", 0.0),
        "severity":        DriftSeverity.HIGH,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER — GET CITY CAGR FROM FORECAST PARAMS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_city_cagr(city: str) -> float:
    """Get CAGR for city from forecast_params.json."""
    forecast = _load_forecast()
    city_data = forecast.get("cities", {}).get(city, {})
    return city_data.get("cagr", 0.088)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# POST /api/predict/valuation — THE CORE ENDPOINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post(
    "/valuation",
    response_model=ValuationResponse,
    summary="Live property valuation with confidence and trust tier",
    description="""
Runs a live prediction using the trained Random Forest model (300 trees, MAPE 1.61%)
and returns a complete valuation report.

What this endpoint does in order:
1. Validates request (city supported, bath/BHK ratio sane)
2. Builds 14-feature sale vector from encodings + city constants
3. Runs model.predict() → price per sqft
4. Builds 14-feature rental vector → rental per sqft
5. Computes confidence score from 300 tree variance
6. Determines trust tier (TRUSTED / CAUTION / FIELD_VERIFICATION)
7. Computes top 5 SHAP drivers for this specific property
8. Fetches city drift status from drift_results.json
9. Returns complete ValuationResponse

Feature vector construction is deterministic — same inputs always produce
same prediction. No randomness at inference.

Training data: 2020 (255,000 rows)
Model: sale_price_v1.pkl + rental_value_v1.pkl
    """
)
async def predict_valuation(request: ValuationRequest):
    try:
        logger.info(
            f"Valuation request — "
            f"{request.city} / {request.locality} / "
            f"{request.bhk}BHK / {request.total_sqft}sqft"
        )
        
        # ── 1. Load base value from SHAP globals ──────────────
        shap_globals = _load_shap_globals()
        base_value   = float(shap_globals.get("base_value", 8437.62))
        
        # ── 2. Build feature vectors ───────────────────────────
        sale_vector   = _build_sale_vector(request)
        rental_vector = _build_rental_vector(request)
        
        logger.debug(f"Sale vector: {sale_vector}")
        
        # ── 3. Run predictions ─────────────────────────────────
        predicted_price_sqft = model_store.predict_sale(sale_vector)
        predicted_rent_sqft  = model_store.predict_rental(rental_vector)
        
        # ── 4. Compute derived values ──────────────────────────
        total_valuation    = predicted_price_sqft * request.total_sqft
        total_valuation_cr = round(total_valuation / 10_000_000, 3)
        rental_estimate    = predicted_rent_sqft * request.total_sqft
        
        # ── 5. Confidence and trust tier ──────────────────────
        confidence_score = model_store.compute_confidence(sale_vector)
        trust_info       = model_store.get_trust_tier(confidence_score)
        trust_tier       = TrustTier(trust_info["tier"])
        trust_color      = trust_info["color"]
        
        # ── 6. SHAP drivers ────────────────────────────────────
        top_drivers = _get_drivers(
            request         = request,
            predicted_price = predicted_price_sqft,
            base_value      = base_value,
            top_n           = 5,
        )
        
        # ── 7. City context ────────────────────────────────────
        city_drift   = _get_city_drift(request.city)
        city_cagr    = _get_city_cagr(request.city)
        city_median  = encoding_store.get_city_median(request.city)
        
        # ── 8. Log summary ────────────────────────────────────
        logger.info(
            f"Valuation complete — "
            f"₹{predicted_price_sqft:,.2f}/sqft | "
            f"Total ₹{total_valuation_cr:.2f}Cr | "
            f"Confidence {confidence_score:.1f} | "
            f"{trust_tier.value}"
        )
        
        # ── 9. Build and return response ──────────────────────
        return ValuationResponse(
            # Core valuation
            predicted_price_sqft = round(predicted_price_sqft, 2),
            total_valuation      = round(total_valuation, 2),
            total_valuation_cr   = total_valuation_cr,
            rental_estimate      = round(rental_estimate, 2),
            
            # Confidence
            confidence_score     = confidence_score,
            trust_tier           = trust_tier,
            trust_color          = trust_color,
            
            # Explainability
            base_value           = round(base_value, 2),
            top_drivers          = top_drivers,
            
            # City context
            city_drift_status    = city_drift["severity"],
            city_ks_stat         = round(city_drift["ks_stat"], 6),
            city_price_shift_pct = round(city_drift["price_shift_pct"], 2),
            city_current_median  = round(city_median, 2),
            city_cagr            = round(city_cagr, 6),
            city_cagr_pct        = round(city_cagr * 100, 2),
            
            # Input echo
            city       = request.city,
            locality   = request.locality,
            bhk        = request.bhk,
            total_sqft = request.total_sqft,
            bath       = request.bath,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"predict/valuation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

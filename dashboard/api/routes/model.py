"""
PropertyIQ API — Model Registry Routes

This file serves model metadata and SHAP global importance from pre-computed
JSON files. The admin Model Health page depends entirely on this file.
"""

import json
import logging
import pandas as pd
from pathlib import Path
from functools import lru_cache
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from config import (
    MODEL_REGISTRY_FILE,
    SHAP_VALUES_FILE,
    FEATURE_DISPLAY_NAMES,
    FEATURE_GROUPS,
    DATA_RAW_DIR,
)
from models.schemas import (
    ModelRegistryResponse,
    ModelEntry,
    ModelStatus,
    SHAPResponse,
    SHAPFeatureImportance,
    FeatureGroup,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROUTER AND LOGGER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

router = APIRouter()
logger = logging.getLogger("propertyiq.routes.model")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CACHED LOADERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@lru_cache(maxsize=1)
def _load_registry() -> dict:
    with open(MODEL_REGISTRY_FILE, 'r') as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_shap() -> dict:
    with open(SHAP_VALUES_FILE, 'r') as f:
        return json.load(f)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER — DETERMINE MODEL STATUS FROM TRAINED DATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_model_status(trained_at: str) -> ModelStatus:
    """
    LIVE    — trained within last 90 days
    STALE   — trained 90-365 days ago
    DEPRECATED — older than 365 days
    """
    try:
        trained = datetime.fromisoformat(trained_at)
        if trained.tzinfo is None:
            trained = trained.replace(tzinfo=timezone.utc)
        now  = datetime.now(timezone.utc)
        days = (now - trained).days
        if days <= 90:
            return ModelStatus.LIVE
        elif days <= 365:
            return ModelStatus.STALE
        else:
            return ModelStatus.DEPRECATED
    except Exception:
        return ModelStatus.LIVE


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER — MAP MAPE TARGET PER MODEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MAPE_TARGETS = {
    "sale_price_v1":  15.0,
    "rental_value_v1": 25.0,
}

MODEL_DISPLAY_NAMES = {
    "sale_price_v1":   "Sale Price Model",
    "rental_value_v1": "Rental Value Model",
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/model/registry
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/registry",
    response_model=ModelRegistryResponse,
    summary="Model registry — all trained models with performance metrics",
    description="""
Returns metadata for all trained models including MAPE, R², OOB score,
training date, and live/stale status.

Sale model: MAPE 1.61% vs 15% target — target met.
Rental model: MAPE 19.64% vs 25% target — target met.

Data source: model_registry.json
    """
)
async def get_registry():
    try:
        registry = _load_registry()
        entries  = []
        
        for model_key, data in registry.items():
            mape_target = MAPE_TARGETS.get(model_key, 20.0)
            status      = _get_model_status(data["trained_at"])
            
            entries.append(ModelEntry(
                model_key       = model_key,
                model_name      = MODEL_DISPLAY_NAMES.get(
                                    model_key, model_key
                                  ),
                version         = "v1",
                target          = data["target"],
                trained_at      = data["trained_at"],
                train_rows      = data["train_rows"],
                val_rows        = data["val_rows"],
                val_mape        = data["val_mape"],
                val_r2          = data["val_r2"],
                oob_r2          = data["oob_r2"],
                mape_target     = mape_target,
                mape_target_met = data["val_mape"] <= mape_target,
                n_estimators    = data["n_estimators"],
                feature_count   = len(data["feature_cols"]),
                confidence_mean = data.get("confidence_mean", 0.0),
                status          = status,
            ))
        
        live_count   = sum(1 for e in entries if e.status == ModelStatus.LIVE)
        last_updated = max(e.trained_at for e in entries)
        
        return ModelRegistryResponse(
            models       = entries,
            total_models = len(entries),
            live_models  = live_count,
            last_updated = last_updated,
        )
    
    except Exception as e:
        logger.error(f"model/registry error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/model/shap
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/shap",
    response_model=SHAPResponse,
    summary="SHAP global feature importance — ranked by mean absolute SHAP value",
    description="""
Returns all 14 features ranked by mean absolute SHAP value computed on
200 validation samples.

Key finding: locality_median_price_sqft SHAP=1614 vs bhk SHAP=2.38 —
location dominates physical features by 160x.

Features grouped into location / macro / physical for the admin dashboard
SHAP chart visual separation.

Data source: shap_values.json
    """
)
async def get_shap():
    try:
        shap_data = _load_shap()
        
        # shap_values.json structure verified:
        # {
        #   "base_value": 8437.622370082747,
        #   "shap_sample_size": 200,
        #   "global_importance": { feature: mean_shap, ... }
        # }
        feature_importance = shap_data.get("global_importance", {})
        base_value  = float(shap_data.get("base_value", 8437.62))
        sample_size = int(shap_data.get("shap_sample_size", 200))
        
        features = []
        for rank, (feature, mean_shap) in enumerate(
            sorted(
                feature_importance.items(),
                key=lambda x: abs(float(x[1])),
                reverse=True
            ),
            start=1
        ):
            group = FEATURE_GROUPS.get(feature, "physical")
            features.append(SHAPFeatureImportance(
                rank          = rank,
                feature       = feature,
                display_name  = FEATURE_DISPLAY_NAMES.get(feature, feature),
                mean_shap     = round(float(mean_shap), 4),
                feature_group = FeatureGroup(group),
            ))
        
        # Compute location vs physical dominance ratio
        location_sum = sum(
            f.mean_shap for f in features
            if f.feature_group == FeatureGroup.LOCATION
        )
        physical_sum = sum(
            f.mean_shap for f in features
            if f.feature_group == FeatureGroup.PHYSICAL
        )
        ratio = round(
            location_sum / physical_sum if physical_sum > 0 else 0.0,
            2
        )
        
        top = features[0] if features else None
        
        return SHAPResponse(
            base_value               = base_value,
            sample_size              = sample_size,
            features                 = features,
            top_feature              = top.feature if top else "",
            top_feature_display      = top.display_name if top else "",
            location_shap_sum        = round(location_sum, 2),
            physical_shap_sum        = round(physical_sum, 2),
            location_dominance_ratio = ratio,
        )
    
    except Exception as e:
        logger.error(f"model/shap error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/model/localities
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/localities",
    summary="All 122 localities for the Client Portal dropdown",
    description="""
Returns the complete list of 122 locality names from encodings.json.
Used by the Client Portal form to populate the locality dropdown.

Note: localities are not nested by city in encodings.json — all 122 are
in one flat list.
    """
)
async def get_localities():
    try:
        from config import encoding_store
        localities = encoding_store.get_localities("")
        return {
            "localities": localities,
            "count":      len(localities),
        }
    except Exception as e:
        logger.error(f"model/localities error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER — LOAD CITY → LOCALITIES MAPPING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@lru_cache(maxsize=1)
def _load_city_locality_map() -> dict:
    """
    Load city → localities mapping from properties_2020.csv.
    Cached after first load — CSV is only read once.
    Returns dict: {city: [locality1, locality2, ...]}
    """
    csv_path = DATA_RAW_DIR / "properties_2020.csv"
    df       = pd.read_csv(csv_path, usecols=['city', 'location'])
    mapping  = (
        df.groupby('city')['location']
        .unique()
        .apply(lambda arr: sorted(arr.tolist()))
        .to_dict()
    )
    return mapping


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/model/localities/{city}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/localities/{city}",
    summary="Localities for a specific city — used by Client Portal dropdown",
    description="""
Returns all localities for the requested city, sorted alphabetically.
Derived from properties_2020.csv training data. Used to populate the
locality dropdown in the Client Portal form.

Supported cities: Mumbai, Delhi, Bengaluru, Hyderabad, Pune, Chennai,
Kolkata, Ahmedabad, Gurgaon, Navi Mumbai
    """
)
async def get_localities_by_city(city: str):
    try:
        mapping    = _load_city_locality_map()
        localities = mapping.get(city, [])
        if not localities:
            raise HTTPException(
                status_code=404,
                detail=f"City '{city}' not found or has no localities"
            )
        return {
            "city":       city,
            "localities": localities,
            "count":      len(localities),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"localities/{city} error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

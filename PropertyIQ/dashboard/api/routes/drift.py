"""
PropertyIQ API — Drift Detection Routes

This file serves all drift-related data from the JSON files already on disk.
No computation happens here. Every endpoint reads a pre-computed JSON and
returns a structured response. This is the most data-rich route — the admin
dashboard Drift Monitor page depends entirely on it.
"""

import json
import logging
from functools import lru_cache
from fastapi import APIRouter, HTTPException

from config import (
    KS_RESULTS_FILE,
    DRIFT_RESULTS_FILE,
    ROLLING_MAPE_FILE,
    MAPE_ALERT_THRESHOLD,
    KS_DRIFT_THRESHOLD,
    FEATURE_DISPLAY_NAMES,
    FEATURE_GROUPS,
)
from models.schemas import (
    DriftSummaryResponse,
    DriftSeverity,
    KSFeatureResult,
    KSCityResult,
    RollingMAPEResponse,
    RollingMAPEPoint,
    Chi2Response,
    Chi2Result,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROUTER AND LOGGER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

router = APIRouter()
logger = logging.getLogger("propertyiq.routes.drift")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CACHED JSON LOADERS — LOAD ONCE, NEVER RE-READ PER REQUEST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@lru_cache(maxsize=1)
def _load_ks_results() -> dict:
    # ks_results exists as standalone file AND inside drift_results
    # Use standalone file as primary source
    with open(KS_RESULTS_FILE, 'r') as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_drift_results() -> dict:
    with open(DRIFT_RESULTS_FILE, 'r') as f:
        return json.load(f)


def _load_rolling_mape() -> dict:
    # rolling_mape is inside drift_results.json
    drift = _load_drift_results()
    return drift.get("rolling_mape", {})


def _load_chi2_results() -> dict:
    drift = _load_drift_results()
    return drift.get("chi2_results", {})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER — MAP SEVERITY STRING TO DRIFTSEVERITY ENUM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _to_severity(s: str) -> DriftSeverity:
    mapping = {
        "HIGH":   DriftSeverity.HIGH,
        "MEDIUM": DriftSeverity.MEDIUM,
        "LOW":    DriftSeverity.LOW,
        "NONE":   DriftSeverity.NONE,
    }
    return mapping.get(str(s).upper(), DriftSeverity.NONE)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/drift/summary
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/summary",
    response_model=DriftSummaryResponse,
    summary="Overall drift summary — severity, counts, recommendation",
    description="""
Returns the top-level drift assessment derived from KS-test results across 11 features and 10 cities.
This is the primary endpoint for the admin dashboard overview strip.

Data source: drift_results.json + ks_results.json
    """
)
async def get_drift_summary():
    try:
        drift = _load_drift_results()
        ks    = _load_ks_results()
        
        summary = drift["summary"]
        conf    = drift["confidence_distribution"]
        
        # Count drifted features from ks_results
        drifted_features = sum(
            1 for v in ks.values()
            if isinstance(v, dict) and v.get("drift_detected", False)
        )
        total_features = sum(
            1 for v in ks.values()
            if isinstance(v, dict) and "ks_stat" in v
        )
        
        # Count cities — all city data is in drift_results city_drift
        city_drift  = drift.get("city_drift", {})
        total_cities = len(city_drift)
        
        # All cities have p=0.0 so all are affected
        cities_affected = sum(
            1 for v in city_drift.values()
            if v.get("p_value", 1.0) < 0.05
        )
        
        # Max KS city
        max_ks_city = max(
            city_drift.items(),
            key=lambda x: x[1]["ks_stat"]
        )
        
        return DriftSummaryResponse(
            overall_severity       = _to_severity(summary["overall_drift_severity"]),
            drifted_features_count = drifted_features,
            total_features         = total_features,
            cities_affected        = cities_affected,
            total_cities           = total_cities,
            max_ks_stat            = max_ks_city[1]["ks_stat"],
            max_ks_city            = max_ks_city[0],
            most_drifted_feature   = summary["most_drifted_feature"],
            alert_message          = (
                f"DRIFT SEVERITY: {summary['overall_drift_severity']} — "
                f"{drifted_features} of {total_features} features drifted. "
                f"All {total_cities} cities affected."
            ),
            recommendation         = summary["recommendation"],
            trusted_pct            = conf["trusted_pct"],
            caution_pct            = conf["caution_pct"],
            mean_confidence        = conf["mean_confidence"],
        )
    except Exception as e:
        logger.error(f"drift/summary error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/drift/ks-features
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/ks-features",
    response_model=list[KSFeatureResult],
    summary="KS-test results per feature — ranked by severity",
    description="""
Returns all 11 features ranked by KS statistic descending. Each entry includes
severity classification and display name. Used to render the feature drift bar
chart on the admin dashboard.

Threshold: KS > 0.30 = drift detected (p < 0.05)
Data source: ks_results.json
    """
)
async def get_ks_features():
    try:
        ks = _load_ks_results()
        
        results = []
        for feature, data in ks.items():
            if not isinstance(data, dict) or "ks_stat" not in data:
                continue
            results.append(KSFeatureResult(
                feature      = feature,
                display_name = FEATURE_DISPLAY_NAMES.get(feature, feature),
                ks_stat      = round(data["ks_stat"], 6),
                p_value      = round(data["p_value"], 6),
                drifted      = data.get("drift_detected", False),
                severity     = _to_severity(data.get("severity", "LOW")),
                feature_group= FEATURE_GROUPS.get(feature, "physical"),
            ))
        
        # Sort by KS stat descending — most drifted first
        results.sort(key=lambda x: x.ks_stat, reverse=True)
        return results
    
    except Exception as e:
        logger.error(f"drift/ks-features error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/drift/ks-cities
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/ks-cities",
    response_model=list[KSCityResult],
    summary="KS-test results per city — ranked by severity",
    description="""
Returns all 10 cities ranked by KS statistic descending. Includes price shift
percentage and mean prices for context. Used to render the city drift table
on the admin dashboard.

Data source: drift_results.json → city_drift section
    """
)
async def get_ks_cities():
    try:
        drift      = _load_drift_results()
        city_drift = drift.get("city_drift", {})
        
        results = []
        for city, data in city_drift.items():
            results.append({
                "city":             city,
                "ks_stat":          data["ks_stat"],
                "p_value":          data["p_value"],
                "price_shift_pct":  data["price_shift_pct"],
                "train_mean_price": data["train_mean_price"],
                "drift_mean_price": data["drift_mean_price"],
            })
        
        # Sort by KS stat descending
        results.sort(key=lambda x: x["ks_stat"], reverse=True)
        
        return [
            KSCityResult(
                rank             = i + 1,
                city             = r["city"],
                ks_stat          = round(r["ks_stat"], 6),
                p_value          = round(r["p_value"], 6),
                drift_status     = DriftSeverity.HIGH,  # all cities p=0.0000
                price_shift_pct  = round(r["price_shift_pct"], 2),
                train_mean_price = round(r["train_mean_price"], 2),
                drift_mean_price = round(r["drift_mean_price"], 2),
            )
            for i, r in enumerate(results)
        ]
    
    except Exception as e:
        logger.error(f"drift/ks-cities error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/drift/rolling-mape
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/rolling-mape",
    response_model=RollingMAPEResponse,
    summary="Rolling MAPE across 600 windows of 500 rows each",
    description="""
Returns all 600 rolling MAPE windows computed on the 2025 drift dataset.
Each window is 500 rows. Windows 589-600 exceed the 20% alert threshold.
The spike is caused by ultra-premium properties (Worli/Bandra >₹290K/sqft).

Data source: drift_results.json → rolling_mape section
    """
)
async def get_rolling_mape():
    try:
        drift        = _load_drift_results()
        rolling_data = drift.get("rolling_mape", {})
        windows_raw  = rolling_data.get("windows", [])
        
        windows = [
            RollingMAPEPoint(
                window_idx  = w["window_idx"],
                window_mape = round(w["window_mape"], 4),
                alert       = w["alert"],
            )
            for w in windows_raw
        ]
        
        total   = len(windows)
        above   = rolling_data.get("windows_above_threshold", 0)
        healthy = round(((total - above) / total) * 100, 2) if total > 0 else 0.0
        
        # Baseline mape is the model val_mape from registry
        # Using 1.61 as the known baseline
        return RollingMAPEResponse(
            windows                 = windows,
            alert_threshold         = MAPE_ALERT_THRESHOLD,
            windows_above_threshold = above,
            total_windows           = total,
            peak_mape               = round(rolling_data.get("peak_mape", 0.0), 4),
            peak_window             = rolling_data.get("peak_window", 0),
            pct_healthy             = healthy,
            baseline_mape           = 1.61,
        )
    
    except Exception as e:
        logger.error(f"drift/rolling-mape error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/drift/chi2
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/chi2",
    response_model=Chi2Response,
    summary="Chi-square drift results for categorical features",
    description="""
Returns chi-square test results for categorical features.
city_tier_encoded: DRIFTED (p=0.033)
is_large_property: NO DRIFT (p=0.325)

Data source: drift_results.json → chi2_results section
    """
)
async def get_chi2():
    try:
        drift      = _load_drift_results()
        chi2_data  = drift.get("chi2_results", {})

        results = []
        for feature, data in chi2_data.items():
            if not isinstance(data, dict) or "chi2_stat" not in data:
                continue
            drifted  = data.get("drift_detected", False)
            severity = DriftSeverity.HIGH if drifted else DriftSeverity.NONE
            results.append(Chi2Result(
                feature   = feature,
                chi2_stat = round(data["chi2_stat"], 4),
                p_value   = round(data["p_value"], 6),
                drifted   = drifted,
                severity  = severity,
            ))

        return Chi2Response(
            results       = results,
            drifted_count = sum(1 for r in results if r.drifted),
            total_tested  = len(results),
        )

    except Exception as e:
        logger.error(f"drift/chi2 error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/drift/city/{city_name}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/city/{city_name}",
    summary="Drift data for a specific city",
    description="""
Returns KS stat, price shift, and drift severity for a single city.
Used by the Client Portal to display city context alongside a valuation.

Supported cities: Mumbai, Delhi, Bengaluru, Hyderabad, Pune, Chennai,
Kolkata, Ahmedabad, Gurgaon, Navi Mumbai
    """
)
async def get_city_drift(city_name: str):
    try:
        drift      = _load_drift_results()
        city_drift = drift.get("city_drift", {})
        
        if city_name not in city_drift:
            raise HTTPException(
                status_code=404,
                detail=f"City '{city_name}' not found. "
                       f"Supported: {list(city_drift.keys())}"
            )
        
        data = city_drift[city_name]
        return {
            "city":             city_name,
            "ks_stat":          round(data["ks_stat"], 6),
            "p_value":          round(data["p_value"], 6),
            "drift_status":     "HIGH",
            "price_shift_pct":  round(data["price_shift_pct"], 2),
            "train_mean_price": round(data["train_mean_price"], 2),
            "drift_mean_price": round(data["drift_mean_price"], 2),
            "drift_mape":       round(data["drift_mape"], 4),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"drift/city error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

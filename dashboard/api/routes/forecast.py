"""
PropertyIQ API — Price Forecast Routes

This file serves city price forecast data computed from implied CAGR between
2020 and 2025 actual medians. All data is pre-computed in forecast_params.json.
No computation happens here except formatting the response. The admin City
Analytics page and the Client Portal city context panel both depend on this file.
"""

import json
import logging
from functools import lru_cache
from fastapi import APIRouter, HTTPException

from config import (
    FORECAST_PARAMS_FILE,
    FORECAST_UNCERTAINTY_PER_YEAR,
    SUPPORTED_CITIES,
)
from models.schemas import (
    CityForecastResponse,
    AllCitiesForecastResponse,
    AllCitiesForecastSummary,
    ForecastPoint,
    ForecastConfidence,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROUTER AND LOGGER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

router = APIRouter()
logger = logging.getLogger("propertyiq.routes.forecast")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CACHED LOADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@lru_cache(maxsize=1)
def _load_forecast_params() -> dict:
    with open(FORECAST_PARAMS_FILE, 'r') as f:
        return json.load(f)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER — COMPUTE FORECAST POINTS FOR A CITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _compute_forecast_points(
    current_median: float,
    cagr: float,
    uncertainty_per_year: float,
) -> list[ForecastPoint]:
    """
    Compute forecast at 5 horizons using implied CAGR.
    
    Formula:
        projected = current * (1 + cagr) ^ years
        lower     = projected * (1 - uncertainty_per_year * years)
        upper     = projected * (1 + uncertainty_per_year * years)
    
    Confidence bands:
        years <= 1  → HIGH
        years <= 3  → MEDIUM
        years >  3  → LOW
    
    uncertainty_per_year = 0.03 (verified from forecast_params.json)
    """
    horizons = [
        (0.5, "+6mo"),
        (1.0, "+1yr"),
        (2.0, "+2yr"),
        (3.0, "+3yr"),
        (5.0, "+5yr"),
    ]
    
    points = []
    for years, label in horizons:
        projected = current_median * ((1 + cagr) ** years)
        lower     = projected * (1 - uncertainty_per_year * years)
        upper     = projected * (1 + uncertainty_per_year * years)
        
        if years <= 1.0:
            confidence = ForecastConfidence.HIGH
        elif years <= 3.0:
            confidence = ForecastConfidence.MEDIUM
        else:
            confidence = ForecastConfidence.LOW
        
        points.append(ForecastPoint(
            horizon_label   = label,
            horizon_years   = years,
            projected_price = round(projected, 2),
            lower_bound     = round(lower, 2),
            upper_bound     = round(upper, 2),
            confidence      = confidence,
        ))
    
    return points


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/forecast/all
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/all",
    response_model=AllCitiesForecastResponse,
    summary="Forecast summary for all 10 cities",
    description="""
Returns a one-row summary per city showing current median, CAGR and
1yr/3yr/5yr projected prices.

Sorted by CAGR descending — highest growth city first.
Data source: forecast_params.json
    """
)
async def get_all_forecasts():
    try:
        params   = _load_forecast_params()
        cities   = params["cities"]
        uncert   = params.get(
            "uncertainty_per_year",
            FORECAST_UNCERTAINTY_PER_YEAR
        )
        
        summaries = []
        for city_name, data in cities.items():
            cagr    = data["cagr"]
            median  = data["median_price_2025"]
            points  = _compute_forecast_points(median, cagr, uncert)
            
            # Index forecast points by horizon label
            by_label = {p.horizon_label: p for p in points}
            
            summaries.append(AllCitiesForecastSummary(
                city             = city_name,
                current_median   = round(median, 2),
                cagr_pct         = round(cagr * 100, 2),
                forecast_1yr     = by_label["+1yr"].projected_price,
                forecast_3yr     = by_label["+3yr"].projected_price,
                forecast_5yr     = by_label["+5yr"].projected_price,
                trend_confidence = data.get("trend_confidence", "MEDIUM"),
            ))
        
        # Sort by CAGR descending
        summaries.sort(key=lambda x: x.cagr_pct, reverse=True)
        
        highest = summaries[0]
        lowest  = summaries[-1]
        
        return AllCitiesForecastResponse(
            cities            = summaries,
            highest_cagr_city = highest.city,
            lowest_cagr_city  = lowest.city,
            highest_cagr_pct  = highest.cagr_pct,
            lowest_cagr_pct   = lowest.cagr_pct,
            total_cities      = len(summaries),
        )
    
    except Exception as e:
        logger.error(f"forecast/all error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GET /api/forecast/{city}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get(
    "/{city}",
    response_model=CityForecastResponse,
    summary="Full forecast detail for a single city",
    description="""
Returns projected prices at 6mo / 1yr / 2yr / 3yr / 5yr horizons for the
requested city, with confidence bands and tier.

Confidence bands widen with horizon:
- <= 1yr  : HIGH   (narrow band)
- <= 3yr  : MEDIUM
- >  3yr  : LOW    (wide band)

Methodology: Implied CAGR from 2020 vs 2025 median price_sqft.
Source: 300,000 observations per year.
Data source: forecast_params.json
    """
)
async def get_city_forecast(city: str):
    try:
        params = _load_forecast_params()
        cities = params["cities"]
        uncert = params.get(
            "uncertainty_per_year",
            FORECAST_UNCERTAINTY_PER_YEAR
        )
        
        if city not in cities:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"City '{city}' not found. "
                    f"Supported: {list(cities.keys())}"
                )
            )
        
        data   = cities[city]
        cagr   = data["cagr"]
        median = data["median_price_2025"]
        points = _compute_forecast_points(median, cagr, uncert)
        
        return CityForecastResponse(
            city             = city,
            current_median   = round(median, 2),
            cagr             = round(cagr, 6),
            cagr_pct         = round(cagr * 100, 2),
            base_year        = 2025,
            forecast_points  = points,
            trend_confidence = data.get("trend_confidence", "MEDIUM"),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"forecast/{city} error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

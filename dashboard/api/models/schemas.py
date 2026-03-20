"""
PropertyIQ FastAPI Backend - Pydantic Schemas

This module defines every Pydantic request and response model used across all API routes.
All routes import from here. Every field is described, validated, and documented for
professional Swagger UI at localhost:8000/docs.

Zero dependencies on config.py — schemas are pure data models.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENUMS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TrustTier(str, Enum):
    """Confidence tier for property valuation predictions."""
    TRUSTED = "TRUSTED"
    CAUTION = "CAUTION"
    FIELD_VERIFICATION = "FIELD_VERIFICATION"


class DriftSeverity(str, Enum):
    """Severity level for data drift detection."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


class ForecastConfidence(str, Enum):
    """Confidence level for future price forecasts."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ModelStatus(str, Enum):
    """Operational status of a trained model."""
    LIVE = "LIVE"
    STALE = "STALE"
    DEPRECATED = "DEPRECATED"


class PropertyType(str, Enum):
    """Type of residential property."""
    APARTMENT = "Apartment"
    VILLA = "Villa"
    INDEPENDENT = "Independent"


class Furnishing(str, Enum):
    """Furnishing status — matches encodings.json furnishing_map keys exactly."""
    UNFURNISHED = "Unfurnished"
    SEMI = "Semi-Furnished"
    FURNISHED = "Fully Furnished"


class FeatureGroup(str, Enum):
    """Feature category for grouping in UI."""
    LOCATION = "location"
    MACRO = "macro"
    PHYSICAL = "physical"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REQUEST SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ValuationRequest(BaseModel):
    """
    Request body for property valuation prediction.
    Used by POST /api/predict/valuation endpoint.
    """
    city: str = Field(
        ...,
        description="One of the 10 supported Indian cities",
        example="Mumbai"
    )
    locality: str = Field(
        ...,
        description="Locality within the selected city — must exist in encodings",
        example="Bandra"
    )
    bhk: int = Field(
        ..., ge=1, le=6,
        description="Number of bedrooms (1 to 6)",
        example=3
    )
    total_sqft: float = Field(
        ..., ge=200.0, le=10000.0,
        description="Total carpet area in square feet",
        example=1200.0
    )
    bath: int = Field(
        ..., ge=1, le=8,
        description="Number of bathrooms",
        example=3
    )
    property_type: PropertyType = Field(
        default=PropertyType.APARTMENT,
        description="Type of property"
    )
    furnishing: Furnishing = Field(
        default=Furnishing.SEMI,
        description="Furnishing status — maps to 0/1/2 encoding"
    )
    
    @validator('city')
    def city_must_be_supported(cls, v):
        """Validate that city is in the supported list."""
        supported = [
            'Mumbai', 'Delhi', 'Bengaluru', 'Hyderabad',
            'Pune', 'Chennai', 'Kolkata', 'Ahmedabad',
            'Gurgaon', 'Navi Mumbai'
        ]
        if v not in supported:
            raise ValueError(
                f"'{v}' is not supported. "
                f"Must be one of: {', '.join(supported)}"
            )
        return v
    
    @validator('bath')
    def bath_reasonable_for_bhk(cls, v, values):
        """Validate that bathroom count is reasonable for given BHK."""
        if 'bhk' in values and v > values['bhk'] + 2:
            raise ValueError(
                f"Bath count {v} is unusually high for {values['bhk']} BHK"
            )
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "city": "Mumbai",
                "locality": "Bandra",
                "bhk": 3,
                "total_sqft": 1200.0,
                "bath": 3,
                "property_type": "Apartment",
                "furnishing": "Semi-Furnished"
            }
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PREDICTION RESPONSE SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SHAPDriver(BaseModel):
    """One feature contribution for the loan officer — explains why this price."""
    feature: str = Field(
        ...,
        description="Raw feature name"
    )
    display_name: str = Field(
        ...,
        description="Plain English label shown to loan officer"
    )
    contribution: float = Field(
        ...,
        description="SHAP contribution in Rs/sqft — positive pushes price up"
    )
    direction: str = Field(
        ...,
        description="UP or DOWN"
    )
    feature_group: str = Field(
        ...,
        description="location / macro / physical"
    )


class ValuationResponse(BaseModel):
    """
    Complete valuation response with prediction, confidence, explainability, and context.
    Returned by POST /api/predict/valuation endpoint.
    """
    # Core valuation numbers
    predicted_price_sqft: float = Field(
        ...,
        description="Predicted price per sqft in Rs"
    )
    total_valuation: float = Field(
        ...,
        description="Total property value in Rs"
    )
    total_valuation_cr: float = Field(
        ...,
        description="Total property value in Crores — shown on UI"
    )
    rental_estimate: float = Field(
        ...,
        description="Monthly rental estimate in Rs"
    )
    
    # Confidence and trust
    confidence_score: float = Field(
        ...,
        description="0 to 100 score derived from tree variance"
    )
    trust_tier: TrustTier = Field(
        ...,
        description="TRUSTED / CAUTION / FIELD_VERIFICATION"
    )
    trust_color: str = Field(
        ...,
        description="Hex color code for trust badge rendering"
    )
    
    # Explainability
    base_value: float = Field(
        ...,
        description="Base market rate Rs/sqft — model expected value"
    )
    top_drivers: List[SHAPDriver] = Field(
        ...,
        description="Top 5 SHAP contributions for this specific prediction"
    )
    
    # City context
    city_drift_status: DriftSeverity = Field(
        ...,
        description="Drift severity for the submitted city"
    )
    city_ks_stat: float = Field(
        ...,
        description="KS statistic for the submitted city"
    )
    city_price_shift_pct: float = Field(
        ...,
        description="Price appreciation percentage for the city 2020 to 2025"
    )
    city_current_median: float = Field(
        ...,
        description="Current city median price per sqft"
    )
    city_cagr: float = Field(
        ...,
        description="City CAGR from 2020 to 2025 as decimal eg 0.088"
    )
    city_cagr_pct: float = Field(
        ...,
        description="City CAGR as percentage eg 8.8"
    )
    
    # Input echo — so frontend does not need to store request
    city: str = Field(..., description="City name (echoed from request)")
    locality: str = Field(..., description="Locality name (echoed from request)")
    bhk: int = Field(..., description="Number of bedrooms (echoed from request)")
    total_sqft: float = Field(..., description="Total area (echoed from request)")
    bath: int = Field(..., description="Number of bathrooms (echoed from request)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DRIFT RESPONSE SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class KSFeatureResult(BaseModel):
    """One row in the feature drift table (KS-test results)."""
    feature: str = Field(..., description="Feature name")
    display_name: str = Field(..., description="Human readable name")
    ks_stat: float = Field(..., description="KS statistic 0 to 1")
    p_value: float = Field(..., description="p-value from ks_2samp")
    drifted: bool = Field(..., description="True if drift_detected flag is set")
    severity: DriftSeverity = Field(..., description="HIGH / MEDIUM / LOW / NONE")
    feature_group: str = Field(..., description="location / macro / physical")


class KSCityResult(BaseModel):
    """One row in the city drift table."""
    rank: int = Field(..., description="Rank 1 = most drifted")
    city: str = Field(..., description="City name")
    ks_stat: float = Field(..., description="KS statistic for this city")
    p_value: float = Field(..., description="p-value")
    drift_status: DriftSeverity = Field(..., description="Drift severity")
    price_shift_pct: float = Field(
        ...,
        description="Price appreciation pct 2020 to 2025"
    )
    train_mean_price: float = Field(
        ...,
        description="Mean price per sqft 2020"
    )
    drift_mean_price: float = Field(
        ...,
        description="Mean price per sqft 2025"
    )


class DriftSummaryResponse(BaseModel):
    """
    Summary of drift detection results.
    Returned by GET /api/drift/summary endpoint.
    """
    overall_severity: DriftSeverity = Field(
        ...,
        description="Overall drift severity across all features"
    )
    drifted_features_count: int = Field(
        ...,
        description="Number of features showing significant drift"
    )
    total_features: int = Field(
        ...,
        description="Total number of features tested"
    )
    cities_affected: int = Field(
        ...,
        description="Number of cities showing drift"
    )
    total_cities: int = Field(
        ...,
        description="Total number of cities"
    )
    max_ks_stat: float = Field(
        ...,
        description="Maximum KS statistic observed"
    )
    max_ks_city: str = Field(
        ...,
        description="City with highest drift"
    )
    most_drifted_feature: str = Field(
        ...,
        description="Feature with highest drift"
    )
    alert_message: str = Field(
        ...,
        description="Human-readable alert message for dashboard"
    )
    recommendation: str = Field(
        ...,
        description="Recommended action based on drift severity"
    )
    trusted_pct: float = Field(
        ...,
        description="Percentage of properties in TRUSTED tier"
    )
    caution_pct: float = Field(
        ...,
        description="Percentage of properties in CAUTION tier"
    )
    mean_confidence: float = Field(
        ...,
        description="Mean confidence score across drift window"
    )


class RollingMAPEPoint(BaseModel):
    """One window in the rolling MAPE analysis."""
    window_idx: int = Field(..., description="Window index (1, 2, 3, ...)")
    window_mape: float = Field(..., description="MAPE percentage for this window")
    alert: bool = Field(..., description="True if MAPE exceeds alert threshold")


class RollingMAPEResponse(BaseModel):
    """
    Rolling MAPE analysis for performance drift detection.
    Returned by GET /api/drift/rolling-mape endpoint.
    """
    windows: List[RollingMAPEPoint] = Field(
        ...,
        description="MAPE data for each window"
    )
    alert_threshold: float = Field(
        ...,
        description="MAPE threshold above which alerts are triggered (20%)"
    )
    windows_above_threshold: int = Field(
        ...,
        description="Number of windows exceeding alert threshold"
    )
    total_windows: int = Field(
        ...,
        description="Total number of windows analyzed"
    )
    peak_mape: float = Field(
        ...,
        description="Highest MAPE observed across all windows"
    )
    peak_window: int = Field(
        ...,
        description="Window index with highest MAPE"
    )
    pct_healthy: float = Field(
        ...,
        description="Percentage of windows below alert threshold"
    )
    baseline_mape: float = Field(
        ...,
        description="Baseline MAPE from validation set"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FORECAST RESPONSE SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ForecastPoint(BaseModel):
    """One forecast horizon point."""
    horizon_label: str = Field(
        ...,
        description="Human-readable horizon label",
        example="+1yr"
    )
    horizon_years: float = Field(
        ...,
        description="Forecast horizon in years"
    )
    projected_price: float = Field(
        ...,
        description="Rs per sqft"
    )
    lower_bound: float = Field(
        ...,
        description="Lower confidence bound"
    )
    upper_bound: float = Field(
        ...,
        description="Upper confidence bound"
    )
    confidence: ForecastConfidence = Field(
        ...,
        description="Confidence level for this horizon"
    )


class CityForecastResponse(BaseModel):
    """
    Forecast for a single city.
    Returned by GET /api/forecast/{city} endpoint.
    """
    city: str = Field(..., description="City name")
    current_median: float = Field(
        ...,
        description="Current median price per sqft (2025)"
    )
    cagr: float = Field(
        ...,
        description="As decimal eg 0.098"
    )
    cagr_pct: float = Field(
        ...,
        description="As percentage eg 9.8"
    )
    base_year: int = Field(
        ...,
        description="Base year for CAGR computation (2020)"
    )
    forecast_points: List[ForecastPoint] = Field(
        ...,
        description="Forecast projections for multiple horizons"
    )
    trend_confidence: str = Field(
        ...,
        description="HIGH / MEDIUM / LOW based on data quality"
    )


class AllCitiesForecastSummary(BaseModel):
    """Summary row for one city in the all-cities forecast table."""
    city: str = Field(..., description="City name")
    current_median: float = Field(
        ...,
        description="Current median price per sqft"
    )
    cagr_pct: float = Field(
        ...,
        description="CAGR as percentage"
    )
    forecast_1yr: float = Field(
        ...,
        description="Projected price in 1 year"
    )
    forecast_3yr: float = Field(
        ...,
        description="Projected price in 3 years"
    )
    forecast_5yr: float = Field(
        ...,
        description="Projected price in 5 years"
    )
    trend_confidence: str = Field(
        ...,
        description="HIGH / MEDIUM / LOW"
    )


class AllCitiesForecastResponse(BaseModel):
    """
    Forecast summary for all cities.
    Returned by GET /api/forecast/all endpoint.
    """
    cities: List[AllCitiesForecastSummary] = Field(
        ...,
        description="Forecast summary for each city"
    )
    highest_cagr_city: str = Field(
        ...,
        description="City with highest CAGR"
    )
    lowest_cagr_city: str = Field(
        ...,
        description="City with lowest CAGR"
    )
    highest_cagr_pct: float = Field(
        ...,
        description="Highest CAGR percentage"
    )
    lowest_cagr_pct: float = Field(
        ...,
        description="Lowest CAGR percentage"
    )
    total_cities: int = Field(
        ...,
        description="Total number of cities"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODEL REGISTRY SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ModelEntry(BaseModel):
    """One row in the model registry table."""
    model_key: str = Field(..., description="Model identifier key")
    model_name: str = Field(..., description="Model display name")
    version: str = Field(..., description="Model version")
    target: str = Field(..., description="Target variable")
    trained_at: str = Field(..., description="Training timestamp")
    train_rows: int = Field(..., description="Number of training rows")
    val_rows: int = Field(..., description="Number of validation rows")
    val_mape: float = Field(..., description="Validation MAPE percentage")
    val_r2: float = Field(..., description="Validation R² score")
    oob_r2: float = Field(..., description="Out-of-bag R² score")
    mape_target: float = Field(..., description="Target MAPE threshold")
    mape_target_met: bool = Field(..., description="True if MAPE target was met")
    n_estimators: int = Field(..., description="Number of trees in forest")
    feature_count: int = Field(..., description="Number of features used")
    confidence_mean: float = Field(..., description="Mean confidence score")
    status: ModelStatus = Field(..., description="Model operational status")


class ModelRegistryResponse(BaseModel):
    """
    Model registry with all trained models.
    Returned by GET /api/model/registry endpoint.
    """
    models: List[ModelEntry] = Field(
        ...,
        description="List of all models in registry"
    )
    total_models: int = Field(
        ...,
        description="Total number of models"
    )
    live_models: int = Field(
        ...,
        description="Number of models with LIVE status"
    )
    last_updated: str = Field(
        ...,
        description="Last registry update timestamp"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHAP SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SHAPFeatureImportance(BaseModel):
    """One row in the SHAP feature importance table."""
    rank: int = Field(..., description="Importance rank (1=most important)")
    feature: str = Field(..., description="Feature name")
    display_name: str = Field(..., description="Human-readable feature name")
    mean_shap: float = Field(..., description="Mean absolute SHAP value")
    feature_group: FeatureGroup = Field(..., description="Feature category")


class SHAPResponse(BaseModel):
    """
    SHAP feature importance analysis.
    Returned by GET /api/model/shap endpoint.
    """
    base_value: float = Field(
        ...,
        description="Base value (expected prediction) in Rs/sqft"
    )
    sample_size: int = Field(
        ...,
        description="Number of samples used for SHAP computation"
    )
    features: List[SHAPFeatureImportance] = Field(
        ...,
        description="Feature importance rankings"
    )
    top_feature: str = Field(
        ...,
        description="Most important feature (raw name)"
    )
    top_feature_display: str = Field(
        ...,
        description="Most important feature (display name)"
    )
    location_shap_sum: float = Field(
        ...,
        description="Sum of SHAP values for location features"
    )
    physical_shap_sum: float = Field(
        ...,
        description="Sum of SHAP values for physical features"
    )
    location_dominance_ratio: float = Field(
        ...,
        description="location SHAP sum divided by physical SHAP sum — shows how much location dominates"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHI-SQUARE SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Chi2Result(BaseModel):
    """One row in the chi-square test results table."""
    feature: str = Field(..., description="Categorical feature name")
    chi2_stat: float = Field(..., description="Chi-square statistic")
    p_value: float = Field(..., description="p-value")
    drifted: bool = Field(..., description="True if drift detected")
    severity: DriftSeverity = Field(..., description="Drift severity")


class Chi2Response(BaseModel):
    """
    Chi-square test results for categorical features.
    Returned by GET /api/drift/chi2 endpoint.
    """
    results: List[Chi2Result] = Field(
        ...,
        description="Chi-square test results for each categorical feature"
    )
    drifted_count: int = Field(
        ...,
        description="Number of features showing drift"
    )
    total_tested: int = Field(
        ...,
        description="Total number of features tested"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UTILITY SCHEMAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LocalitiesResponse(BaseModel):
    """
    List of localities for a given city.
    Used to populate frontend dropdown. Returned by GET /api/localities/{city}.
    """
    localities: List[str] = Field(
        ...,
        description="List of locality names in alphabetical order"
    )
    count: int = Field(
        ...,
        description="Total number of localities"
    )


class AlertItem(BaseModel):
    """One row in the alert log."""
    severity: str = Field(
        ...,
        description="HIGH / WARN / INFO / OK"
    )
    timestamp: str = Field(
        ...,
        description="Alert timestamp (ISO format)"
    )
    message: str = Field(
        ...,
        description="Human-readable alert message"
    )
    source: str = Field(
        ...,
        description="Which JSON file this was derived from"
    )


class AlertLogResponse(BaseModel):
    """
    Alert log with all system alerts.
    Returned by GET /api/alerts endpoint.
    """
    alerts: List[AlertItem] = Field(
        ...,
        description="List of all alerts"
    )
    total: int = Field(
        ...,
        description="Total number of alerts"
    )
    high_count: int = Field(
        ...,
        description="Number of HIGH severity alerts"
    )
    warn_count: int = Field(
        ...,
        description="Number of WARN severity alerts"
    )
    info_count: int = Field(
        ...,
        description="Number of INFO severity alerts"
    )
    ok_count: int = Field(
        ...,
        description="Number of OK severity alerts"
    )


class HealthResponse(BaseModel):
    """
    System health check response.
    Returned by GET /health endpoint.
    """
    status: str = Field(
        ...,
        description="Overall system status: healthy / degraded / down"
    )
    models_loaded: bool = Field(
        ...,
        description="True if models loaded successfully"
    )
    encodings_loaded: bool = Field(
        ...,
        description="True if encodings loaded successfully"
    )
    outputs_verified: int = Field(
        ...,
        description="Number of output JSON files found"
    )
    version: str = Field(
        default="1.0.0",
        description="API version"
    )

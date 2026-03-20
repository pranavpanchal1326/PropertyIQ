# PropertyIQ API Models

This directory contains all Pydantic schemas used across the FastAPI backend.

## Files

### `schemas.py`
Complete Pydantic model definitions for all API requests and responses.

**Zero dependencies on config.py** — schemas are pure data models that can be imported anywhere.

### `test_schemas.py`
Comprehensive test suite that validates:
- All enum values are correct
- Request validators work properly
- Response schemas can be instantiated
- Furnishing enum matches encodings.json exactly

Run tests:
```bash
python PropertyIQ/dashboard/api/models/test_schemas.py
```

### `__init__.py`
Empty file to make this directory a Python package.

## Schema Categories

### Enums (7 total)
- `TrustTier` — TRUSTED / CAUTION / FIELD_VERIFICATION
- `DriftSeverity` — HIGH / MEDIUM / LOW / NONE
- `ForecastConfidence` — HIGH / MEDIUM / LOW
- `ModelStatus` — LIVE / STALE / DEPRECATED
- `PropertyType` — Apartment / Villa / Independent
- `Furnishing` — Unfurnished / Semi-Furnished / Fully Furnished
- `FeatureGroup` — location / macro / physical

### Request Schemas (1 total)
- `ValuationRequest` — POST /api/predict/valuation body

### Response Schemas (20+ total)

**Prediction:**
- `SHAPDriver` — One feature contribution row
- `ValuationResponse` — Complete valuation with confidence and explainability

**Drift Detection:**
- `KSFeatureResult` — One row in feature drift table
- `KSCityResult` — One row in city drift table
- `DriftSummaryResponse` — Overall drift summary
- `RollingMAPEPoint` — One window in rolling MAPE
- `RollingMAPEResponse` — Complete rolling MAPE analysis

**Forecasting:**
- `ForecastPoint` — One forecast horizon
- `CityForecastResponse` — Forecast for single city
- `AllCitiesForecastSummary` — Summary row for one city
- `AllCitiesForecastResponse` — All cities forecast

**Model Registry:**
- `ModelEntry` — One model in registry
- `ModelRegistryResponse` — Complete model registry

**SHAP Analysis:**
- `SHAPFeatureImportance` — One feature importance row
- `SHAPResponse` — Complete SHAP analysis

**Chi-Square:**
- `Chi2Result` — One chi-square test result
- `Chi2Response` — All chi-square results

**Utilities:**
- `LocalitiesResponse` — Localities for dropdown
- `AlertItem` — One alert log entry
- `AlertLogResponse` — Complete alert log
- `HealthResponse` — System health check

## Validation Rules

### ValuationRequest Validators

**City validator:**
- Must be one of 10 supported cities
- Error message lists all supported cities

**Bath validator:**
- Bath count cannot exceed BHK + 2
- Error message shows actual values

**Numeric bounds:**
- `bhk`: 1 to 6
- `total_sqft`: 200 to 10,000
- `bath`: 1 to 8

## Furnishing Enum

The `Furnishing` enum values MUST match `encodings.json` furnishing_map keys exactly:

```json
{
  "furnishing_map": {
    "Unfurnished": 0,
    "Semi-Furnished": 1,
    "Fully Furnished": 2
  }
}
```

Enum definition:
```python
class Furnishing(str, Enum):
    UNFURNISHED = "Unfurnished"
    SEMI = "Semi-Furnished"
    FURNISHED = "Fully Furnished"
```

This is verified by `test_schemas.py`.

## Swagger UI Documentation

Every field has a `description` parameter that appears in Swagger UI at `localhost:8000/docs`.

Example:
```python
city: str = Field(
    ...,
    description="One of the 10 supported Indian cities",
    example="Mumbai"
)
```

This makes the API self-documenting and professional.

## Usage in Routes

Routes import schemas like this:

```python
from dashboard.api.models.schemas import (
    ValuationRequest,
    ValuationResponse,
    TrustTier,
    DriftSeverity
)

@router.post("/valuation", response_model=ValuationResponse)
async def predict_valuation(request: ValuationRequest):
    # FastAPI automatically validates request body
    # and serializes response using schemas
    ...
```

## Testing

All schemas are tested in `test_schemas.py`:

```bash
python PropertyIQ/dashboard/api/models/test_schemas.py
```

Expected output:
```
████████████████████████████████████████████████████████████
PropertyIQ Schemas Test Suite
████████████████████████████████████████████████████████████

============================================================
TEST: Enums
============================================================
✓ TrustTier enum
✓ DriftSeverity enum
...

ALL TESTS PASSED ✓
```

## Design Principles

1. **Zero dependencies** — schemas.py imports only from pydantic and typing
2. **Every field documented** — professional Swagger UI
3. **Proper validation** — clear error messages
4. **Type safety** — full type hints
5. **Enum consistency** — matches encodings.json exactly
6. **Testable** — comprehensive test suite included

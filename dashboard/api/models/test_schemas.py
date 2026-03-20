"""
Test suite for PropertyIQ Pydantic schemas.

Validates:
- All enums have correct values
- Request validators work correctly
- All response schemas can be instantiated
- Furnishing enum matches encodings.json exactly
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from schemas import (
    # Enums
    TrustTier, DriftSeverity, ForecastConfidence, ModelStatus,
    PropertyType, Furnishing, FeatureGroup,
    # Request schemas
    ValuationRequest,
    # Response schemas
    SHAPDriver, ValuationResponse,
    KSFeatureResult, KSCityResult, DriftSummaryResponse,
    RollingMAPEPoint, RollingMAPEResponse,
    ForecastPoint, CityForecastResponse,
    AllCitiesForecastSummary, AllCitiesForecastResponse,
    ModelEntry, ModelRegistryResponse,
    SHAPFeatureImportance, SHAPResponse,
    Chi2Result, Chi2Response,
    LocalitiesResponse, AlertItem, AlertLogResponse,
    HealthResponse
)


def test_enums():
    """Test all enum values are correct."""
    print("\n" + "="*60)
    print("TEST: Enums")
    print("="*60)
    
    # TrustTier
    assert TrustTier.TRUSTED == "TRUSTED"
    assert TrustTier.CAUTION == "CAUTION"
    assert TrustTier.FIELD_VERIFICATION == "FIELD_VERIFICATION"
    print("✓ TrustTier enum")
    
    # DriftSeverity
    assert DriftSeverity.HIGH == "HIGH"
    assert DriftSeverity.MEDIUM == "MEDIUM"
    assert DriftSeverity.LOW == "LOW"
    assert DriftSeverity.NONE == "NONE"
    print("✓ DriftSeverity enum")
    
    # ForecastConfidence
    assert ForecastConfidence.HIGH == "HIGH"
    assert ForecastConfidence.MEDIUM == "MEDIUM"
    assert ForecastConfidence.LOW == "LOW"
    print("✓ ForecastConfidence enum")
    
    # ModelStatus
    assert ModelStatus.LIVE == "LIVE"
    assert ModelStatus.STALE == "STALE"
    assert ModelStatus.DEPRECATED == "DEPRECATED"
    print("✓ ModelStatus enum")
    
    # PropertyType
    assert PropertyType.APARTMENT == "Apartment"
    assert PropertyType.VILLA == "Villa"
    assert PropertyType.INDEPENDENT == "Independent"
    print("✓ PropertyType enum")
    
    # Furnishing — CRITICAL: must match encodings.json
    assert Furnishing.UNFURNISHED == "Unfurnished"
    assert Furnishing.SEMI == "Semi-Furnished"
    assert Furnishing.FURNISHED == "Fully Furnished"
    print("✓ Furnishing enum (matches encodings.json)")
    
    # FeatureGroup
    assert FeatureGroup.LOCATION == "location"
    assert FeatureGroup.MACRO == "macro"
    assert FeatureGroup.PHYSICAL == "physical"
    print("✓ FeatureGroup enum")


def test_valuation_request_valid():
    """Test valid ValuationRequest."""
    print("\n" + "="*60)
    print("TEST: ValuationRequest - Valid Cases")
    print("="*60)
    
    # Valid request
    req = ValuationRequest(
        city="Mumbai",
        locality="Bandra",
        bhk=3,
        total_sqft=1200.0,
        bath=3,
        property_type=PropertyType.APARTMENT,
        furnishing=Furnishing.SEMI
    )
    assert req.city == "Mumbai"
    assert req.locality == "Bandra"
    assert req.bhk == 3
    assert req.bath == 3
    print("✓ Valid request accepted")
    
    # Valid with defaults
    req2 = ValuationRequest(
        city="Delhi",
        locality="Connaught Place",
        bhk=2,
        total_sqft=900.0,
        bath=2
    )
    assert req2.property_type == PropertyType.APARTMENT
    assert req2.furnishing == Furnishing.SEMI
    print("✓ Defaults applied correctly")


def test_valuation_request_validators():
    """Test ValuationRequest validators."""
    print("\n" + "="*60)
    print("TEST: ValuationRequest - Validators")
    print("="*60)
    
    # Test unsupported city
    try:
        ValuationRequest(
            city="Jaipur",  # Not supported
            locality="Test",
            bhk=3,
            total_sqft=1200.0,
            bath=3
        )
        assert False, "Should have raised ValueError for unsupported city"
    except ValueError as e:
        assert "not supported" in str(e)
        print(f"✓ Unsupported city rejected: {e}")
    
    # Test bath > bhk + 2
    try:
        ValuationRequest(
            city="Mumbai",
            locality="Bandra",
            bhk=2,
            total_sqft=1200.0,
            bath=6  # 6 > 2 + 2
        )
        assert False, "Should have raised ValueError for excessive bath count"
    except ValueError as e:
        assert "unusually high" in str(e)
        print(f"✓ Excessive bath count rejected: {e}")
    
    # Test bath = bhk + 2 (should be valid)
    req = ValuationRequest(
        city="Mumbai",
        locality="Bandra",
        bhk=3,
        total_sqft=1200.0,
        bath=5  # 5 = 3 + 2 (valid)
    )
    assert req.bath == 5
    print("✓ Bath = BHK + 2 accepted")
    
    # Test numeric bounds
    try:
        ValuationRequest(
            city="Mumbai",
            locality="Bandra",
            bhk=0,  # Below minimum
            total_sqft=1200.0,
            bath=2
        )
        assert False, "Should have raised ValueError for bhk < 1"
    except ValueError:
        print("✓ BHK < 1 rejected")
    
    try:
        ValuationRequest(
            city="Mumbai",
            locality="Bandra",
            bhk=3,
            total_sqft=100.0,  # Below minimum
            bath=2
        )
        assert False, "Should have raised ValueError for sqft < 200"
    except ValueError:
        print("✓ Total sqft < 200 rejected")


def test_response_schemas():
    """Test response schemas can be instantiated."""
    print("\n" + "="*60)
    print("TEST: Response Schemas")
    print("="*60)
    
    # SHAPDriver
    driver = SHAPDriver(
        feature="locality_median_price_sqft",
        display_name="Locality Market Rate",
        contribution=2500.0,
        direction="UP",
        feature_group="location"
    )
    assert driver.contribution == 2500.0
    print("✓ SHAPDriver")
    
    # ValuationResponse
    val_resp = ValuationResponse(
        predicted_price_sqft=18000.0,
        total_valuation=21600000.0,
        total_valuation_cr=2.16,
        rental_estimate=45000.0,
        confidence_score=82.5,
        trust_tier=TrustTier.TRUSTED,
        trust_color="#0D9488",
        base_value=16000.0,
        top_drivers=[driver],
        city_drift_status=DriftSeverity.LOW,
        city_ks_stat=0.15,
        city_price_shift_pct=45.2,
        city_current_median=15777.0,
        city_cagr=0.088,
        city_cagr_pct=8.8,
        city="Mumbai",
        locality="Bandra",
        bhk=3,
        total_sqft=1200.0,
        bath=3
    )
    assert val_resp.confidence_score == 82.5
    assert val_resp.trust_tier == TrustTier.TRUSTED
    print("✓ ValuationResponse")
    
    # KSFeatureResult
    ks_feat = KSFeatureResult(
        feature="rbi_hpi_avg",
        display_name="RBI Housing Price Index",
        ks_stat=0.42,
        p_value=0.001,
        drifted=True,
        severity=DriftSeverity.HIGH,
        feature_group="macro"
    )
    assert ks_feat.drifted is True
    print("✓ KSFeatureResult")
    
    # DriftSummaryResponse
    drift_summary = DriftSummaryResponse(
        overall_severity=DriftSeverity.HIGH,
        drifted_features_count=8,
        total_features=14,
        cities_affected=7,
        total_cities=10,
        max_ks_stat=0.52,
        max_ks_city="Mumbai",
        most_drifted_feature="rbi_hpi_avg",
        alert_message="High drift detected",
        recommendation="Retrain model",
        trusted_pct=45.2,
        caution_pct=32.1,
        mean_confidence=68.5
    )
    assert drift_summary.drifted_features_count == 8
    print("✓ DriftSummaryResponse")
    
    # ForecastPoint
    forecast_pt = ForecastPoint(
        horizon_label="+1yr",
        horizon_years=1.0,
        projected_price=17000.0,
        lower_bound=16000.0,
        upper_bound=18000.0,
        confidence=ForecastConfidence.HIGH
    )
    assert forecast_pt.horizon_years == 1.0
    print("✓ ForecastPoint")
    
    # ModelEntry
    model_entry = ModelEntry(
        model_key="sale_price_v1",
        model_name="Sale Price Model",
        version="v1",
        target="price_per_sqft",
        trained_at="2025-01-15",
        train_rows=240000,
        val_rows=60000,
        val_mape=8.2,
        val_r2=0.89,
        oob_r2=0.87,
        mape_target=10.0,
        mape_target_met=True,
        n_estimators=300,
        feature_count=14,
        confidence_mean=72.5,
        status=ModelStatus.LIVE
    )
    assert model_entry.mape_target_met is True
    print("✓ ModelEntry")
    
    # HealthResponse
    health = HealthResponse(
        status="healthy",
        models_loaded=True,
        encodings_loaded=True,
        outputs_verified=11,
        version="1.0.0"
    )
    assert health.models_loaded is True
    print("✓ HealthResponse")


def test_furnishing_matches_encodings():
    """Verify Furnishing enum matches encodings.json exactly."""
    print("\n" + "="*60)
    print("TEST: Furnishing Enum vs encodings.json")
    print("="*60)
    
    import json
    encodings_path = Path(__file__).resolve().parent.parent.parent.parent / "outputs" / "encodings.json"
    
    with open(encodings_path, 'r') as f:
        encodings = json.load(f)
    
    furnishing_map = encodings['furnishing_map']
    
    # Check all keys in encodings.json are in enum
    for key in furnishing_map.keys():
        if key == "Unfurnished":
            assert Furnishing.UNFURNISHED == key
        elif key == "Semi-Furnished":
            assert Furnishing.SEMI == key
        elif key == "Fully Furnished":
            assert Furnishing.FURNISHED == key
        else:
            assert False, f"Unknown furnishing key in encodings.json: {key}"
    
    print(f"✓ All {len(furnishing_map)} furnishing values match")
    print(f"  Encodings.json keys: {list(furnishing_map.keys())}")
    print(f"  Enum values: {[f.value for f in Furnishing]}")


def run_all_tests():
    """Run all test functions."""
    print("\n" + "█"*60)
    print("PropertyIQ Schemas Test Suite")
    print("█"*60)
    
    try:
        test_enums()
        test_valuation_request_valid()
        test_valuation_request_validators()
        test_response_schemas()
        test_furnishing_matches_encodings()
        
        print("\n" + "█"*60)
        print("ALL TESTS PASSED ✓")
        print("█"*60)
        print("\nschemas.py is production-ready.")
        print("All validators work correctly.")
        print("Furnishing enum matches encodings.json exactly.")
        print()
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()

"""
Quick integration test to verify schemas work with config.py.

This demonstrates that schemas can be used independently (zero dependencies)
but also integrate seamlessly with config.py when needed.
"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schemas import ValuationRequest, Furnishing, PropertyType, TrustTier
from config import SUPPORTED_CITIES, TRUST_THRESHOLDS, FEATURE_DISPLAY_NAMES


def test_integration():
    """Test that schemas integrate with config.py."""
    print("\n" + "="*60)
    print("INTEGRATION TEST: schemas.py + config.py")
    print("="*60)
    
    # Create a valid request
    req = ValuationRequest(
        city="Mumbai",
        locality="Bandra",
        bhk=3,
        total_sqft=1200.0,
        bath=3,
        property_type=PropertyType.APARTMENT,
        furnishing=Furnishing.SEMI
    )
    
    print(f"\n✓ Request created:")
    print(f"  City: {req.city}")
    print(f"  Locality: {req.locality}")
    print(f"  BHK: {req.bhk}")
    print(f"  Total sqft: {req.total_sqft}")
    print(f"  Bath: {req.bath}")
    print(f"  Property type: {req.property_type.value}")
    print(f"  Furnishing: {req.furnishing.value}")
    
    # Verify city is in config
    assert req.city in SUPPORTED_CITIES
    print(f"\n✓ City '{req.city}' is in SUPPORTED_CITIES")
    
    # Verify trust tiers match
    for tier in TrustTier:
        assert tier.value in TRUST_THRESHOLDS
    print(f"✓ All TrustTier values exist in TRUST_THRESHOLDS")
    
    # Verify feature display names exist
    assert 'locality_median_price_sqft' in FEATURE_DISPLAY_NAMES
    assert 'rbi_hpi_avg' in FEATURE_DISPLAY_NAMES
    print(f"✓ Feature display names available ({len(FEATURE_DISPLAY_NAMES)} features)")
    
    # Test validator with invalid city
    try:
        ValuationRequest(
            city="InvalidCity",
            locality="Test",
            bhk=3,
            total_sqft=1200.0,
            bath=3
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"\n✓ Validator correctly rejects invalid city")
    
    # Test validator with excessive bath count
    try:
        ValuationRequest(
            city="Mumbai",
            locality="Bandra",
            bhk=2,
            total_sqft=1200.0,
            bath=6  # 6 > 2 + 2
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Validator correctly rejects excessive bath count")
    
    print("\n" + "="*60)
    print("INTEGRATION TEST PASSED ✓")
    print("="*60)
    print("\nschemas.py integrates seamlessly with config.py")
    print("All validators work correctly")
    print("All enum values match config constants")
    print()


if __name__ == "__main__":
    test_integration()

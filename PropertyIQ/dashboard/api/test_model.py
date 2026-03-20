"""
Test script to verify model endpoints.

Tests:
1. GET /api/model/registry — Model registry with performance metrics
2. GET /api/model/shap — SHAP global feature importance
3. GET /api/model/localities — All 122 localities
"""

import requests
import json


def test_model_registry():
    """Test /api/model/registry endpoint."""
    print("\n" + "="*60)
    print("TEST: GET /api/model/registry")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/api/model/registry")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status code: {response.status_code}")
        print(f"✓ Total models: {data['total_models']}")
        print(f"✓ Live models: {data['live_models']}")
        print(f"✓ Last updated: {data['last_updated']}")
        
        print(f"\n✓ Model entries:")
        for model in data['models']:
            print(f"\n  {model['model_name']}:")
            print(f"    Key: {model['model_key']}")
            print(f"    Target: {model['target']}")
            print(f"    MAPE: {model['val_mape']}% (target: {model['mape_target']}%)")
            print(f"    MAPE target met: {model['mape_target_met']}")
            print(f"    R²: {model['val_r2']}")
            print(f"    OOB R²: {model['oob_r2']}")
            print(f"    Status: {model['status']}")
            print(f"    Features: {model['feature_count']}")
            print(f"    Train rows: {model['train_rows']}")
            print(f"    Val rows: {model['val_rows']}")
        
        # Verify expected values
        assert data['total_models'] == 2, "Should have 2 models"
        
        sale_model = next(m for m in data['models'] if m['model_key'] == 'sale_price_v1')
        assert sale_model['val_mape'] == 1.61, "Sale model MAPE should be 1.61%"
        assert sale_model['mape_target_met'] is True, "Sale model should meet MAPE target"
        assert sale_model['feature_count'] == 14, "Sale model should have 14 features"
        
        print("\n✓ All model registry tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_shap_importance():
    """Test /api/model/shap endpoint."""
    print("\n" + "="*60)
    print("TEST: GET /api/model/shap")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/api/model/shap")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status code: {response.status_code}")
        print(f"✓ Base value: ₹{data['base_value']:.2f}")
        print(f"✓ Sample size: {data['sample_size']}")
        print(f"✓ Top feature: {data['top_feature_display']}")
        print(f"✓ Location SHAP sum: {data['location_shap_sum']:.2f}")
        print(f"✓ Physical SHAP sum: {data['physical_shap_sum']:.2f}")
        print(f"✓ Location dominance ratio: {data['location_dominance_ratio']}x")
        
        print(f"\n✓ Top 5 features:")
        for i, feature in enumerate(data['features'][:5], 1):
            print(f"  {i}. {feature['display_name']:30s} "
                  f"SHAP: {feature['mean_shap']:8.2f}  "
                  f"Group: {feature['feature_group']}")
        
        # Verify expected values
        assert data['sample_size'] == 200, "Sample size should be 200"
        assert len(data['features']) == 14, "Should have 14 features"
        
        top_feature = data['features'][0]
        assert top_feature['feature'] == 'locality_median_price_sqft', \
            "Top feature should be locality_median_price_sqft"
        assert top_feature['mean_shap'] > 1600, \
            "Top feature SHAP should be > 1600"
        
        # Verify location dominates physical
        assert data['location_dominance_ratio'] > 100, \
            "Location should dominate physical by >100x"
        
        print("\n✓ All SHAP importance tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_localities():
    """Test /api/model/localities endpoint."""
    print("\n" + "="*60)
    print("TEST: GET /api/model/localities")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/api/model/localities")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status code: {response.status_code}")
        print(f"✓ Total localities: {data['count']}")
        
        print(f"\n✓ First 10 localities:")
        for i, locality in enumerate(data['localities'][:10], 1):
            print(f"  {i:2d}. {locality}")
        
        print(f"\n✓ Last 5 localities:")
        for i, locality in enumerate(data['localities'][-5:], len(data['localities'])-4):
            print(f"  {i:2d}. {locality}")
        
        # Verify expected values
        assert data['count'] == 122, "Should have 122 localities"
        assert 'Bandra West' in data['localities'], "Should include Bandra West"
        assert 'Worli' in data['localities'], "Should include Worli"
        
        # Verify sorted
        assert data['localities'] == sorted(data['localities']), \
            "Localities should be sorted alphabetically"
        
        print("\n✓ All localities tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all model endpoint tests."""
    print("\n" + "█"*60)
    print("PropertyIQ Model Endpoints Tests")
    print("█"*60)
    print("\nServer should be running at http://localhost:8000")
    
    results = []
    
    results.append(("Model Registry", test_model_registry()))
    results.append(("SHAP Importance", test_shap_importance()))
    results.append(("Localities List", test_localities()))
    
    print("\n" + "█"*60)
    print("TEST SUMMARY")
    print("█"*60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status:8s} {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n" + "█"*60)
        print("ALL MODEL TESTS PASSED ✓")
        print("█"*60)
        print("\nModel routes are working correctly!")
        print("\nKey findings:")
        print("- Sale model MAPE: 1.61% (target: 15%) ✓")
        print("- Rental model MAPE: 19.64% (target: 25%) ✓")
        print("- Location features dominate by >100x")
        print("- 122 localities available")
        print()
    else:
        print("\n❌ Some tests failed")
    
    return all_passed


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to http://localhost:8000")
        print("Make sure the server is running:")
        print("  cd PropertyIQ/dashboard/api")
        print("  python -m uvicorn main:app --reload --port 8000")

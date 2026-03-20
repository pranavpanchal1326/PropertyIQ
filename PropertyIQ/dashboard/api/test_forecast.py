"""
Test script to verify forecast endpoints.

Tests:
1. GET /api/forecast/all — All cities summary
2. GET /api/forecast/Bengaluru — Single city detail
3. GET /api/forecast/Mumbai — Single city detail
"""

import requests
import json


def test_forecast_all():
    """Test /api/forecast/all endpoint."""
    print("\n" + "="*60)
    print("TEST: GET /api/forecast/all")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/api/forecast/all")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status code: {response.status_code}")
        print(f"✓ Total cities: {data['total_cities']}")
        print(f"✓ Highest CAGR city: {data['highest_cagr_city']} ({data['highest_cagr_pct']}%)")
        print(f"✓ Lowest CAGR city: {data['lowest_cagr_city']} ({data['lowest_cagr_pct']}%)")
        
        print(f"\n✓ First 3 cities (sorted by CAGR desc):")
        for i, city in enumerate(data['cities'][:3], 1):
            print(f"  {i}. {city['city']:15s} CAGR: {city['cagr_pct']:5.2f}%  "
                  f"Current: ₹{city['current_median']:8.2f}  "
                  f"+5yr: ₹{city['forecast_5yr']:8.2f}")
        
        # Verify expected values
        first_city = data['cities'][0]
        last_city = data['cities'][-1]
        
        print(f"\n✓ Verification:")
        print(f"  First city: {first_city['city']} with CAGR {first_city['cagr_pct']}%")
        print(f"  Last city: {last_city['city']} with CAGR {last_city['cagr_pct']}%")
        
        # Expected: Hyderabad first (~10.84%), Kolkata last (~5.6%)
        assert first_city['cagr_pct'] > 10.0, "First city should have CAGR > 10%"
        assert last_city['cagr_pct'] < 7.0, "Last city should have CAGR < 7%"
        
        print("\n✓ All forecast/all tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_forecast_bengaluru():
    """Test /api/forecast/Bengaluru endpoint."""
    print("\n" + "="*60)
    print("TEST: GET /api/forecast/Bengaluru")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/api/forecast/Bengaluru")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status code: {response.status_code}")
        print(f"✓ City: {data['city']}")
        print(f"✓ Current median: ₹{data['current_median']:.2f}")
        print(f"✓ CAGR: {data['cagr_pct']:.2f}%")
        print(f"✓ Base year: {data['base_year']}")
        print(f"✓ Trend confidence: {data['trend_confidence']}")
        
        print(f"\n✓ Forecast points:")
        for point in data['forecast_points']:
            print(f"  {point['horizon_label']:6s} "
                  f"₹{point['projected_price']:8.2f}  "
                  f"[₹{point['lower_bound']:8.2f} - ₹{point['upper_bound']:8.2f}]  "
                  f"{point['confidence']}")
        
        # Verify expected values
        # Expected: current ~10362, +1yr ~11378, +5yr ~16537
        assert 10000 < data['current_median'] < 11000, "Current median should be ~10362"
        
        one_yr = next(p for p in data['forecast_points'] if p['horizon_label'] == '+1yr')
        five_yr = next(p for p in data['forecast_points'] if p['horizon_label'] == '+5yr')
        
        assert 11000 < one_yr['projected_price'] < 12000, "+1yr should be ~11378"
        assert 16000 < five_yr['projected_price'] < 17000, "+5yr should be ~16537"
        
        print("\n✓ All Bengaluru forecast tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_forecast_mumbai():
    """Test /api/forecast/Mumbai endpoint."""
    print("\n" + "="*60)
    print("TEST: GET /api/forecast/Mumbai")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/api/forecast/Mumbai")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status code: {response.status_code}")
        print(f"✓ City: {data['city']}")
        print(f"✓ Current median: ₹{data['current_median']:.2f}")
        print(f"✓ CAGR: {data['cagr_pct']:.2f}%")
        
        print(f"\n✓ Forecast points:")
        for point in data['forecast_points']:
            print(f"  {point['horizon_label']:6s} "
                  f"₹{point['projected_price']:8.2f}  "
                  f"[₹{point['lower_bound']:8.2f} - ₹{point['upper_bound']:8.2f}]  "
                  f"{point['confidence']}")
        
        # Verify expected values
        # Expected: current ~24065, +5yr ~36700
        assert 23000 < data['current_median'] < 25000, "Current median should be ~24065"
        
        five_yr = next(p for p in data['forecast_points'] if p['horizon_label'] == '+5yr')
        assert 35000 < five_yr['projected_price'] < 38000, "+5yr should be ~36700"
        
        print("\n✓ All Mumbai forecast tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_forecast_invalid_city():
    """Test /api/forecast/{city} with invalid city."""
    print("\n" + "="*60)
    print("TEST: GET /api/forecast/InvalidCity (should 404)")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/api/forecast/InvalidCity")
        
        if response.status_code == 404:
            print(f"✓ Status code: {response.status_code} (expected)")
            error = response.json()
            print(f"✓ Error message: {error['detail']}")
            print("\n✓ Invalid city correctly rejected")
            return True
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def run_all_tests():
    """Run all forecast endpoint tests."""
    print("\n" + "█"*60)
    print("PropertyIQ Forecast Endpoints Tests")
    print("█"*60)
    print("\nServer should be running at http://localhost:8000")
    
    results = []
    
    results.append(("Forecast All Cities", test_forecast_all()))
    results.append(("Forecast Bengaluru", test_forecast_bengaluru()))
    results.append(("Forecast Mumbai", test_forecast_mumbai()))
    results.append(("Invalid City 404", test_forecast_invalid_city()))
    
    print("\n" + "█"*60)
    print("TEST SUMMARY")
    print("█"*60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status:8s} {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n" + "█"*60)
        print("ALL FORECAST TESTS PASSED ✓")
        print("█"*60)
        print("\nForecast routes are working correctly!")
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

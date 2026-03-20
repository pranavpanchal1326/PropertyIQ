"""
Test script to verify PropertyIQ API endpoints.

Tests the three verification steps:
1. /health endpoint
2. / root endpoint
3. /docs availability
"""

import requests
import json


def test_health():
    """Test /health endpoint."""
    print("\n" + "="*60)
    print("TEST 1: /health endpoint")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/health")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status code: {response.status_code}")
        print(f"✓ Response:")
        print(json.dumps(data, indent=2))
        
        # Verify expected fields
        assert data["status"] == "healthy", f"Expected healthy, got {data['status']}"
        assert data["models_loaded"] is True, "Models not loaded"
        assert data["encodings_loaded"] is True, "Encodings not loaded"
        assert data["outputs_verified"] == 11, f"Expected 11 outputs, got {data['outputs_verified']}"
        
        print("\n✓ All health checks passed")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_root():
    """Test / root endpoint."""
    print("\n" + "="*60)
    print("TEST 2: / root endpoint")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status code: {response.status_code}")
        print(f"✓ Service: {data['service']}")
        print(f"✓ Version: {data['version']}")
        print(f"✓ Status: {data['status']}")
        print(f"\n✓ Available endpoints:")
        for key, path in data['endpoints'].items():
            print(f"  - {key:10s} → {path}")
        
        # Verify expected fields
        assert data["service"] == "PropertyIQ API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "endpoints" in data
        
        print("\n✓ Root endpoint test passed")
        return True
        
    except Exception as e:
        print(f"❌ Root endpoint test failed: {e}")
        return False


def test_docs():
    """Test /docs endpoint availability."""
    print("\n" + "="*60)
    print("TEST 3: /docs endpoint (Swagger UI)")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/docs")
        response.raise_for_status()
        
        print(f"✓ Status code: {response.status_code}")
        print(f"✓ Content type: {response.headers.get('content-type')}")
        print(f"✓ Swagger UI is accessible at http://localhost:8000/docs")
        
        # Check that it's HTML
        assert "text/html" in response.headers.get("content-type", "")
        
        print("\n✓ Swagger UI test passed")
        return True
        
    except Exception as e:
        print(f"❌ Swagger UI test failed: {e}")
        return False


def test_openapi_schema():
    """Test OpenAPI schema endpoint."""
    print("\n" + "="*60)
    print("TEST 4: /openapi.json schema")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        response.raise_for_status()
        
        schema = response.json()
        print(f"✓ Status code: {response.status_code}")
        print(f"✓ OpenAPI version: {schema.get('openapi')}")
        print(f"✓ API title: {schema['info']['title']}")
        print(f"✓ API version: {schema['info']['version']}")
        
        # Check for route tags
        tags = [tag['name'] for tag in schema.get('tags', [])]
        print(f"\n✓ Route tags found:")
        for tag in tags:
            print(f"  - {tag}")
        
        expected_tags = [
            "Drift Detection",
            "Price Forecast",
            "Model Registry",
            "SHAP Explainability",
            "Valuation Engine",
            "System"
        ]
        
        for tag in expected_tags:
            if tag in tags:
                print(f"  ✓ {tag}")
            else:
                print(f"  ⚠ {tag} (not found)")
        
        print("\n✓ OpenAPI schema test passed")
        return True
        
    except Exception as e:
        print(f"❌ OpenAPI schema test failed: {e}")
        return False


def run_all_tests():
    """Run all endpoint tests."""
    print("\n" + "█"*60)
    print("PropertyIQ API Endpoint Tests")
    print("█"*60)
    print("\nServer should be running at http://localhost:8000")
    
    results = []
    
    results.append(("Health Check", test_health()))
    results.append(("Root Endpoint", test_root()))
    results.append(("Swagger UI", test_docs()))
    results.append(("OpenAPI Schema", test_openapi_schema()))
    
    print("\n" + "█"*60)
    print("TEST SUMMARY")
    print("█"*60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status:8s} {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n" + "█"*60)
        print("ALL TESTS PASSED ✓")
        print("█"*60)
        print("\nPhase 1 backend foundation is complete!")
        print("Open http://localhost:8000/docs to see Swagger UI")
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

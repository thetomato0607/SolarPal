"""
VPP Integration Test Suite
===========================
Verifies that the VPP engine is properly integrated and working.
"""

import sys
from datetime import datetime


def test_vpp_engine():
    """Test VPP optimizer core functionality."""
    print("\n" + "="*70)
    print("TEST 1: VPP Engine Import & Optimization")
    print("="*70)

    try:
        from vpp_engine import VPPOptimizer, generate_uk_price_profile, generate_load_profile

        # Create optimizer
        optimizer = VPPOptimizer(
            battery_capacity_kwh=13.5,
            battery_power_kw=5.0,
            battery_efficiency=0.90,
            grid_export_limit_kw=4.0
        )
        print("[PASS] VPP optimizer instantiated")

        # Generate test data
        N = 96
        start_time = datetime(2025, 12, 1, 0, 0)

        import numpy as np
        hours = np.array([(start_time.hour + i*0.25) for i in range(N)])
        solar_kw = (2.5 * np.exp(-((hours - 12)**2) / (2 * 2.5**2))).tolist()
        load_kw = generate_load_profile(start_time, N, 10.0)
        price_gbp_kwh = generate_uk_price_profile(start_time, N)

        print(f"[PASS] Generated {N} intervals of test data")

        # Run optimization
        result = optimizer.optimize(
            solar_kw=solar_kw,
            load_kw=load_kw,
            price_gbp_per_kwh=price_gbp_kwh,
            initial_soc_pct=50.0
        )

        print(f"[PASS] Optimization completed successfully")
        print(f"  Revenue: {result['revenue_gbp']:.2f} GBP")
        print(f"  Cost: {result['energy_cost_gbp']:.2f} GBP")
        print(f"  Net Profit: {result['net_profit_gbp']:.2f} GBP")

        # Verify constraints
        max_export = max(result['grid_export_kw'])
        print(f"\n  Max grid export: {max_export:.3f} kW")
        print(f"  Grid limit: {optimizer.grid_limit:.3f} kW")

        if max_export <= optimizer.grid_limit + 1e-6:
            print(f"[PASS] Grid constraint satisfied: {max_export:.3f} <= {optimizer.grid_limit}")
        else:
            print(f"[FAIL] Grid constraint violated!")
            return False

        # Check SoC bounds
        min_soc = min(result['soc_pct'])
        max_soc = max(result['soc_pct'])
        if 0 <= min_soc and max_soc <= 100:
            print(f"[PASS] Battery SoC within bounds: [{min_soc:.1f}%, {max_soc:.1f}%]")
        else:
            print(f"[FAIL] Battery SoC out of bounds!")
            return False

        return True

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_routes():
    """Test that API routes are properly configured."""
    print("\n" + "="*70)
    print("TEST 2: API Route Configuration")
    print("="*70)

    try:
        from routes import vpp
        print("[PASS] VPP routes module imported")

        # Check router exists
        if hasattr(vpp, 'router'):
            print("[PASS] VPP router exists")
        else:
            print("[FAIL] VPP router not found")
            return False

        # Check endpoints
        routes = [r.path for r in vpp.router.routes]
        expected = ['/optimize', '/simulate', '/benchmark', '/health']

        for endpoint in expected:
            if endpoint in routes:
                print(f"[PASS] Endpoint exists: {endpoint}")
            else:
                print(f"[FAIL] Endpoint missing: {endpoint}")
                return False

        return True

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_models():
    """Test that Pydantic models are properly defined."""
    print("\n" + "="*70)
    print("TEST 3: Pydantic Models")
    print("="*70)

    try:
        from models import (
            VPPOptimizationRequest,
            VPPOptimizationResult,
            GridImpactAnalysis,
            VPPSimulationResponse
        )

        print("[PASS] All VPP models imported")

        # Test model instantiation
        request = VPPOptimizationRequest(
            solar_forecast_kw=[0.5] * 96,
            battery_capacity_kwh=13.5
        )
        print("[PASS] VPPOptimizationRequest model instantiated")

        return True

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_integration():
    """Test that VPP is integrated in main.py."""
    print("\n" + "="*70)
    print("TEST 4: Main App Integration")
    print("="*70)

    try:
        from main import app

        # Check VPP router is included
        routes = [r.path for r in app.routes]
        vpp_routes = [r for r in routes if r.startswith('/vpp')]

        if len(vpp_routes) > 0:
            print(f"[PASS] Found {len(vpp_routes)} VPP routes in main app")
            for route in vpp_routes[:5]:  # Show first 5
                print(f"  - {route}")
        else:
            print("[FAIL] No VPP routes found in main app")
            return False

        return True

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run complete test suite."""
    print("\n" + "="*70)
    print(" VPP INTEGRATION TEST SUITE ".center(70, "="))
    print("="*70)

    tests = [
        ("VPP Engine", test_vpp_engine),
        ("API Routes", test_api_routes),
        ("Pydantic Models", test_models),
        ("Main Integration", test_main_integration)
    ]

    results = []
    for name, test_func in tests:
        passed = test_func()
        results.append((name, passed))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed_count = sum(1 for _, passed in results if passed)
    total = len(results)

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")

    print("="*70)
    print(f"Results: {passed_count}/{total} tests passed")

    if passed_count == total:
        print("\n[SUCCESS] All tests passed! Your VPP is ready to use.")
        print("\nNext steps:")
        print("  1. Start server: uvicorn main:app --reload")
        print("  2. Visit docs: http://localhost:8000/docs")
        print("  3. Test endpoint: curl http://localhost:8000/vpp/simulate")
        return 0
    else:
        print(f"\n[ERROR] {total - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

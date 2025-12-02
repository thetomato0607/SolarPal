#!/usr/bin/env python3
"""
Integration Test - SolarPal Live Data
======================================
Test that live data flows correctly through the entire system.
"""

from modules.market_data import MarketDataGenerator
from modules.live_data import OctopusEnergyAPI
from datetime import datetime

def test_live_data_integration():
    """Test complete live data flow."""
    print("\n" + "="*70)
    print("SOLARPAL LIVE DATA INTEGRATION TEST")
    print("="*70)

    # Test 1: Direct API fetch
    print("\n[TEST 1] Testing direct API fetch...")
    try:
        prices = OctopusEnergyAPI.fetch_agile_prices(region='A')
        if prices and len(prices) == 96:
            print(f"✅ API fetch successful: {len(prices)} intervals")
            print(f"   Price range: £{min(prices):.4f} - £{max(prices):.4f}/kWh")
        else:
            print(f"❌ API fetch failed or incomplete data")
            return False
    except Exception as e:
        print(f"❌ API fetch error: {e}")
        return False

    # Test 2: Market data generator with live prices
    print("\n[TEST 2] Testing MarketDataGenerator with live prices...")
    try:
        market_gen = MarketDataGenerator(
            use_live_prices=True,
            octopus_region='A'
        )

        scenario = market_gen.generate_scenario(
            system_size_kwp=3.5,
            daily_load_kwh=12.0,
            volatility_multiplier=1.5,
            cloud_cover_factor=0.3,
            start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        )

        if scenario and len(scenario.price_gbp_kwh) == 96:
            print(f"✅ Scenario generation successful")
            print(f"   Data source: {scenario.price_data_source}")
            print(f"   Region: {scenario.price_region}")
            print(f"   Price range: £{min(scenario.price_gbp_kwh):.4f} - £{max(scenario.price_gbp_kwh):.4f}/kWh")

            if scenario.price_data_source == "octopus_agile":
                print(f"✅ Live data successfully integrated!")
                return True
            else:
                print(f"⚠️  Fell back to synthetic data")
                return False
        else:
            print(f"❌ Scenario generation failed")
            return False

    except Exception as e:
        print(f"❌ Scenario generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 3: Synthetic fallback
    print("\n[TEST 3] Testing synthetic fallback...")
    try:
        market_gen = MarketDataGenerator(
            use_live_prices=False,  # Force synthetic
            octopus_region='A'
        )

        scenario = market_gen.generate_scenario(
            system_size_kwp=3.5,
            daily_load_kwh=12.0,
            volatility_multiplier=1.5,
            cloud_cover_factor=0.3
        )

        if scenario and scenario.price_data_source == "synthetic":
            print(f"✅ Synthetic fallback working correctly")
            return True
        else:
            print(f"❌ Synthetic fallback failed")
            return False

    except Exception as e:
        print(f"❌ Synthetic fallback error: {e}")
        return False


def main():
    """Run integration tests."""
    success = test_live_data_integration()

    print("\n" + "="*70)
    if success:
        print("🎉 SUCCESS! Live data integration is working!")
        print("\nYou can now run your SolarPal app:")
        print("   streamlit run app.py")
        print("\nMake sure to:")
        print("   1. Check 'Use Live UK Prices (Octopus Agile)'")
        print("   2. Select your region")
        print("   3. Click 'RUN OPTIMIZATION'")
    else:
        print("⚠️  Some tests failed. Check errors above.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

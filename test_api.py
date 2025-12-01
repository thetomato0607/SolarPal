#!/usr/bin/env python3
"""
Octopus Energy API Test Script
===============================
Standalone test to verify API connection and data fetching.

Run this BEFORE integrating into your main app to verify everything works.

Usage:
    python test_octopus_api.py
"""

import requests
from datetime import datetime, timedelta
import json


def test_1_list_products():
    """Test 1: List available Octopus Energy products."""
    print("\n" + "="*70)
    print("TEST 1: Listing Available Products")
    print("="*70)
    
    try:
        url = "https://api.octopus.energy/v1/products/"
        params = {
            'is_variable': 'true',
            'available_at': datetime.now().isoformat()
        }
        
        print(f"URL: {url}")
        print(f"Params: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('results', [])
            
            print(f"\n✅ Found {len(products)} products")
            
            # Find Agile products
            agile_products = [p for p in products if 'AGILE' in p['code'].upper()]
            
            if agile_products:
                print(f"\n🎯 Agile Products:")
                for product in agile_products[:3]:  # Show first 3
                    print(f"  - {product['code']}")
                    print(f"    Name: {product.get('display_name', 'N/A')}")
                    print(f"    Available: {product.get('available_from', 'N/A')} to {product.get('available_to', 'Ongoing')}")
            else:
                print("\n⚠️  No Agile products found")
            
            return True
        else:
            print(f"\n❌ Failed: Status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_2_fetch_current_prices():
    """Test 2: Fetch current half-hour prices."""
    print("\n" + "="*70)
    print("TEST 2: Fetching Current Agile Prices")
    print("="*70)
    
    try:
        # Use the LATEST Agile tariff code
        region = 'A'  # Eastern England
        tariff_code = f"E-1R-AGILE-FLEX-22-11-25-{region}"
        
        url = (
            f"https://api.octopus.energy/v1/products/"
            f"AGILE-FLEX-22-11-25/electricity-tariffs/"
            f"{tariff_code}/standard-unit-rates/"
        )
        
        # Get last 24 hours
        now = datetime.now()
        period_from = now - timedelta(hours=24)
        
        params = {
            'period_from': period_from.isoformat(),
            'period_to': now.isoformat(),
            'page_size': 100
        }
        
        print(f"URL: {url}")
        print(f"Tariff: {tariff_code}")
        print(f"Period: {period_from.strftime('%Y-%m-%d %H:%M')} to {now.strftime('%Y-%m-%d %H:%M')}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"\n✅ Fetched {len(results)} half-hourly prices")
            
            if results:
                # Show first 5 prices
                print(f"\n📊 Sample Prices (newest first):")
                for i, price in enumerate(results[:5]):
                    valid_from = price['valid_from'][:16]  # Truncate to minutes
                    value = price['value_inc_vat'] / 100  # Convert pence to pounds
                    print(f"  {valid_from}: £{value:.4f}/kWh")
                
                # Statistics
                import numpy as np
                prices = [r['value_inc_vat'] / 100 for r in results]
                print(f"\n📈 24-Hour Statistics:")
                print(f"  Min:  £{np.min(prices):.4f}/kWh")
                print(f"  Max:  £{np.max(prices):.4f}/kWh")
                print(f"  Mean: £{np.mean(prices):.4f}/kWh")
                print(f"  Std:  £{np.std(prices):.4f}/kWh")
                
                # Price range check
                price_range = np.max(prices) - np.min(prices)
                if price_range > 0.10:
                    print(f"\n💰 Good arbitrage opportunity! Range: £{price_range:.4f}/kWh")
                else:
                    print(f"\n⚠️  Low volatility day. Range: £{price_range:.4f}/kWh")
            
            return True
            
        elif response.status_code == 404:
            print(f"\n❌ Tariff not found: {tariff_code}")
            print(f"   This region may not have Agile available.")
            print(f"   Try region 'A' (Eastern England)")
            return False
        else:
            print(f"\n❌ Failed: Status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_fetch_24h_forecast():
    """Test 3: Fetch full 24-hour price forecast."""
    print("\n" + "="*70)
    print("TEST 3: Fetching 24-Hour Price Forecast")
    print("="*70)
    
    try:
        region = 'A'
        tariff_code = f"E-1R-AGILE-FLEX-22-11-25-{region}"
        
        url = (
            f"https://api.octopus.energy/v1/products/"
            f"AGILE-FLEX-22-11-25/electricity-tariffs/"
            f"{tariff_code}/standard-unit-rates/"
        )
        
        # Get today midnight to tomorrow midnight
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        params = {
            'period_from': today.isoformat(),
            'period_to': tomorrow.isoformat(),
            'page_size': 100
        }
        
        print(f"Fetching prices from {today.strftime('%Y-%m-%d')} (96 intervals)...")
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = list(reversed(data.get('results', [])))  # Oldest first
            
            print(f"\n✅ Fetched {len(results)} half-hourly prices")
            
            if len(results) >= 48:  # 48 half-hours = 24 hours
                # Convert to 15-min intervals (duplicate each)
                prices_15min = []
                for r in results[:48]:
                    price_gbp = r['value_inc_vat'] / 100
                    prices_15min.extend([price_gbp, price_gbp])
                
                print(f"✅ Converted to {len(prices_15min)} 15-min intervals")
                
                # Find best charge/discharge windows
                import numpy as np
                prices_array = np.array(prices_15min)
                
                # Best times to charge (lowest 10%)
                cheap_threshold = np.percentile(prices_array, 10)
                cheap_times = np.where(prices_array <= cheap_threshold)[0]
                
                # Best times to discharge (highest 10%)
                expensive_threshold = np.percentile(prices_array, 90)
                expensive_times = np.where(prices_array >= expensive_threshold)[0]
                
                print(f"\n💡 Trading Opportunities:")
                print(f"   Charge when price < £{cheap_threshold:.4f}/kWh")
                print(f"   Discharge when price > £{expensive_threshold:.4f}/kWh")
                print(f"   Potential spread: £{expensive_threshold - cheap_threshold:.4f}/kWh")
                
                # Estimate profit
                battery_capacity = 13.5  # kWh
                cycles_per_day = 1
                arbitrage_profit = (expensive_threshold - cheap_threshold) * battery_capacity * cycles_per_day
                
                print(f"\n💰 Daily Arbitrage Potential:")
                print(f"   Battery: {battery_capacity} kWh")
                print(f"   Spread: £{expensive_threshold - cheap_threshold:.4f}/kWh")
                print(f"   Profit: £{arbitrage_profit:.2f}/day (1 cycle)")
                print(f"   Annual: £{arbitrage_profit * 365:.0f}/year")
                
                return True
            else:
                print(f"\n⚠️  Only {len(results)} prices available (need 48 for 24h)")
                return False
                
        else:
            print(f"\n❌ Failed: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_all_regions():
    """Test 4: Check which regions have Agile available."""
    print("\n" + "="*70)
    print("TEST 4: Checking Agile Availability by Region")
    print("="*70)
    
    regions = {
        'A': 'Eastern England',
        'B': 'East Midlands',
        'C': 'London',
        'D': 'Merseyside and Northern Wales',
        'E': 'West Midlands',
        'F': 'North Eastern England',
        'G': 'North Western England',
        'H': 'Southern England',
        'J': 'South Eastern England',
        'K': 'Southern Wales',
        'L': 'South Western England',
        'M': 'Yorkshire',
        'N': 'Southern Scotland',
        'P': 'Northern Scotland'
    }
    
    print(f"\nChecking {len(regions)} regions...")
    
    available = []
    unavailable = []
    
    for code, name in regions.items():
        tariff_code = f"E-1R-AGILE-FLEX-22-11-25-{code}"
        url = (
            f"https://api.octopus.energy/v1/products/"
            f"AGILE-FLEX-22-11-25/electricity-tariffs/"
            f"{tariff_code}/standard-unit-rates/"
        )
        
        try:
            response = requests.get(url, params={'page_size': 1}, timeout=5)
            if response.status_code == 200:
                available.append((code, name))
                print(f"  ✅ {code}: {name}")
            else:
                unavailable.append((code, name))
                print(f"  ❌ {code}: {name} (not available)")
        except:
            unavailable.append((code, name))
            print(f"  ⚠️  {code}: {name} (timeout)")
    
    print(f"\n📊 Summary:")
    print(f"   Available: {len(available)} regions")
    print(f"   Unavailable: {len(unavailable)} regions")
    
    if available:
        print(f"\n💡 Recommended regions for testing:")
        for code, name in available[:3]:
            print(f"   - {code}: {name}")
    
    return len(available) > 0


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("OCTOPUS ENERGY API TEST SUITE")
    print("="*70)
    print("\nTesting connection to Octopus Energy API...")
    print("No API key required - this is public data")
    print("="*70)
    
    # Run tests
    results = {
        "List Products": test_1_list_products(),
        "Fetch Current Prices": test_2_fetch_current_prices(),
        "Fetch 24h Forecast": test_3_fetch_24h_forecast(),
        "Check All Regions": test_4_all_regions()
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS! Octopus Energy API is working perfectly.")
        print("\nYou can now integrate this into your VPP Trading Terminal:")
        print("  1. Copy live_data.py to modules/")
        print("  2. Update market_data.py with enhanced version")
        print("  3. Add integration code to app.py")
        print("  4. Run: streamlit run app.py")
    elif passed > 0:
        print("\n⚠️  PARTIAL SUCCESS. Some tests passed.")
        print("Check error messages above for details.")
    else:
        print("\n❌ ALL TESTS FAILED")
        print("Possible issues:")
        print("  - No internet connection")
        print("  - Octopus API is down")
        print("  - Firewall blocking requests")
        print("  - Invalid tariff codes (Octopus may have updated)")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
# coding: utf-8
"""
Live Market Data Integration
=============================
Fetch real-time UK electricity prices from Octopus Energy.

API Documentation: https://developer.octopus.energy/docs/api/
"""

import requests
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import streamlit as st


class OctopusEnergyAPI:
    """
    Client for Octopus Energy API - fetches real UK electricity prices.
    
    NO API KEY REQUIRED for public tariff data!
    
    Supported tariffs:
    - Agile Octopus: Half-hourly pricing linked to wholesale market
    - Tracker: Daily pricing tracking wholesale costs
    - Flexible: Standard variable tariff
    """
    
    BASE_URL = "https://api.octopus.energy/v1"
    
    # Current Agile tariff codes by region
    # See: https://octopus.energy/agile/
    AGILE_REGIONS = {
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
    
    @staticmethod
    def list_available_products(is_variable: bool = True) -> Optional[List[Dict]]:
        """
        List all available Octopus Energy products.
        
        Args:
            is_variable: Filter for variable tariffs only
            
        Returns:
            List of products with codes and names
        """
        try:
            url = f"{OctopusEnergyAPI.BASE_URL}/products/"
            params = {
                'is_variable': str(is_variable).lower(),
                'available_at': datetime.now().isoformat()
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                print(f"Failed to fetch products: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching products: {e}")
            return None
    
    @staticmethod
    def get_latest_agile_product() -> Optional[str]:
        """
        Automatically detect the latest Agile product code.

        Returns:
            Latest Agile product code (e.g. 'AGILE-24-10-01') or None
        """
        try:
            products = OctopusEnergyAPI.list_available_products()
            if products:
                # Find all Agile products
                agile_products = [p for p in products if 'AGILE' in p['code'].upper() and 'OUTGOING' not in p['code'].upper()]
                if agile_products:
                    # Return the first (most recent) one
                    return agile_products[0]['code']
            return None
        except:
            return None

    @staticmethod
    def get_agile_tariff_code(region: str = 'A') -> str:
        """
        Get the current Agile Octopus tariff code for a region.

        Args:
            region: Region code (A-P)

        Returns:
            Tariff code like 'E-1R-AGILE-24-10-01-A'
        """
        # Try to get latest product code dynamically
        product_code = OctopusEnergyAPI.get_latest_agile_product()

        # Fallback to known working codes
        if not product_code:
            product_code = "AGILE-24-10-01"  # Current as of Dec 2024

        return f"E-1R-{product_code}-{region}"
    
    @staticmethod
    def fetch_agile_prices(
        date: datetime = None,
        region: str = 'A',
        hours: int = 24
    ) -> Optional[List[float]]:
        """
        Fetch Agile Octopus half-hourly prices for specified period.
        
        Args:
            date: Start date (defaults to today midnight)
            region: Region code (A-P, default A = Eastern England)
            hours: Number of hours to fetch (default 24)
            
        Returns:
            List of 96 prices in £/kWh for 15-min intervals, or None if fetch fails
            
        Example:
            >>> prices = OctopusEnergyAPI.fetch_agile_prices()
            >>> print(f"Current price: £{prices[0]:.4f}/kWh")
        """
        try:
            # Default to today midnight
            if date is None:
                date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Get product code and tariff code for region
            product_code = OctopusEnergyAPI.get_latest_agile_product()
            if not product_code:
                product_code = "AGILE-24-10-01"  # Fallback

            tariff_code = OctopusEnergyAPI.get_agile_tariff_code(region)

            # Build API URL
            url = (
                f"{OctopusEnergyAPI.BASE_URL}/products/"
                f"{product_code}/electricity-tariffs/"
                f"{tariff_code}/standard-unit-rates/"
            )
            
            # Set time window
            period_from = date
            period_to = date + timedelta(hours=hours)
            
            params = {
                'period_from': period_from.isoformat(),
                'period_to': period_to.isoformat(),
                'page_size': 100  # Ensure we get all data
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    print("No price data returned from API")
                    return None
                
                # API returns newest first, so reverse
                results = list(reversed(results))
                
                # Extract prices and convert pence to pounds
                prices_halfhourly = [r['value_inc_vat'] / 100 for r in results]

                # Convert 30-min to 15-min intervals (duplicate each value)
                prices_15min = []
                for price in prices_halfhourly:
                    prices_15min.extend([price, price])

                # If we don't have enough data for full 24 hours, try yesterday
                if len(prices_15min) < 96:
                    print(f"Only {len(prices_15min)} intervals available for {date.date()}, trying yesterday...")
                    yesterday = date - timedelta(days=1)
                    yesterday_prices = OctopusEnergyAPI.fetch_agile_prices(yesterday, region, hours)
                    if yesterday_prices and len(yesterday_prices) >= 96:
                        return yesterday_prices[:96]

                # Return what we have, padded if necessary
                if len(prices_15min) < 96:
                    # Pad with last known price
                    last_price = prices_15min[-1] if prices_15min else 0.15
                    prices_15min.extend([last_price] * (96 - len(prices_15min)))

                return prices_15min[:96]
            
            elif response.status_code == 404:
                print(f"Tariff not found. Region '{region}' may not have Agile available.")
                print("Try region 'A' (Eastern England) or check https://octopus.energy/agile/")
                return None
            
            else:
                print(f"API returned status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            print("Request timed out. Octopus API may be slow.")
            return None
            
        except requests.exceptions.ConnectionError:
            print("Connection error. Check internet connection.")
            return None
            
        except Exception as e:
            print(f"Error fetching Agile prices: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def get_current_price(region: str = 'A') -> Optional[float]:
        """
        Get the current half-hour price for right now.

        Args:
            region: Region code (A-P)

        Returns:
            Current price in £/kWh, or None if unavailable
        """
        try:
            # Fetch from midnight today to get full day's prices
            now = datetime.now()
            midnight_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            prices = OctopusEnergyAPI.fetch_agile_prices(midnight_today, region, hours=24)

            if prices:
                # Calculate which 15-min interval we're in
                current_interval = (now.hour * 4) + (now.minute // 15)
                if current_interval < len(prices):
                    return prices[current_interval]

            return None

        except Exception as e:
            print(f"Error getting current price: {e}")
            return None
    
    @staticmethod
    def get_price_statistics(
        region: str = 'A',
        days: int = 7
    ) -> Optional[Dict[str, float]]:
        """
        Get price statistics over recent days.
        
        Args:
            region: Region code
            days: Number of days to analyze
            
        Returns:
            Dictionary with min, max, mean, std of prices
        """
        try:
            import numpy as np
            
            all_prices = []
            for day in range(days):
                date = datetime.now() - timedelta(days=day)
                date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                
                prices = OctopusEnergyAPI.fetch_agile_prices(date, region, hours=24)
                if prices:
                    all_prices.extend(prices)
            
            if not all_prices:
                return None
            
            prices_array = np.array(all_prices)
            
            return {
                'min_gbp_kwh': float(np.min(prices_array)),
                'max_gbp_kwh': float(np.max(prices_array)),
                'mean_gbp_kwh': float(np.mean(prices_array)),
                'std_gbp_kwh': float(np.std(prices_array)),
                'p10_gbp_kwh': float(np.percentile(prices_array, 10)),
                'p90_gbp_kwh': float(np.percentile(prices_array, 90))
            }
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return None


# Convenience functions for Streamlit
def display_live_price_widget(region: str = 'A'):
    """
    Display live price in Streamlit sidebar.
    
    Usage:
        display_live_price_widget('A')
    """
    current_price = OctopusEnergyAPI.get_current_price(region)
    
    if current_price:
        # Color code based on price
        if current_price < 0.05:
            emoji = "🟢"
            color = "green"
        elif current_price < 0.10:
            emoji = "🟡"
            color = "orange"
        else:
            emoji = "🔴"
            color = "red"
        
        st.sidebar.markdown(
            f"{emoji} **Live Price:** "
            f"<span style='color:{color};font-size:20px;'>"
            f"£{current_price:.4f}/kWh"
            f"</span>",
            unsafe_allow_html=True
        )
        
        region_name = OctopusEnergyAPI.AGILE_REGIONS.get(region, region)
        st.sidebar.caption(f"Octopus Agile • {region_name}")
        
        return current_price
    else:
        st.sidebar.warning("⚠️ Live prices unavailable")
        return None


def test_api_connection():
    """
    Test Octopus Energy API connection.
    Run this to verify everything works.
    """
    print("\n" + "="*70)
    print("TESTING OCTOPUS ENERGY API")
    print("="*70)
    
    # Test 1: Fetch products
    print("\n[TEST 1] Fetching available products...")
    products = OctopusEnergyAPI.list_available_products()
    if products:
        print(f"✅ Found {len(products)} products")
        agile_products = [p for p in products if 'AGILE' in p['code']]
        if agile_products:
            print(f"✅ Agile product found: {agile_products[0]['code']}")
        else:
            print("⚠️  No Agile products found")
    else:
        print("❌ Failed to fetch products")
    
    # Test 2: Fetch current price
    print("\n[TEST 2] Fetching current price for Region A...")
    current_price = OctopusEnergyAPI.get_current_price('A')
    if current_price:
        print(f"✅ Current price: £{current_price:.4f}/kWh")
    else:
        print("❌ Failed to fetch current price")
    
    # Test 3: Fetch 24h prices
    print("\n[TEST 3] Fetching 24-hour price profile...")
    prices = OctopusEnergyAPI.fetch_agile_prices(region='A')
    if prices:
        import numpy as np
        print(f"✅ Fetched {len(prices)} intervals")
        print(f"   Min: £{np.min(prices):.4f}/kWh")
        print(f"   Max: £{np.max(prices):.4f}/kWh")
        print(f"   Avg: £{np.mean(prices):.4f}/kWh")
    else:
        print("❌ Failed to fetch 24h prices")
    
    # Test 4: Statistics
    print("\n[TEST 4] Calculating 7-day price statistics...")
    stats = OctopusEnergyAPI.get_price_statistics('A', days=7)
    if stats:
        print(f"✅ 7-day statistics:")
        print(f"   Min: £{stats['min_gbp_kwh']:.4f}/kWh")
        print(f"   Max: £{stats['max_gbp_kwh']:.4f}/kWh")
        print(f"   Mean: £{stats['mean_gbp_kwh']:.4f}/kWh")
        print(f"   Std: £{stats['std_gbp_kwh']:.4f}/kWh")
    else:
        print("⚠️  Statistics unavailable")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run tests when executed directly
    test_api_connection()
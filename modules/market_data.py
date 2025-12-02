# coding: utf-8
"""
Market Data Generator (Enhanced with Live Data)
================================================
Realistic UK energy market simulation with optional live price fetching.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from dataclasses import dataclass

# Import live data API
try:
    from .live_data import OctopusEnergyAPI
    LIVE_DATA_AVAILABLE = True
except ImportError:
    LIVE_DATA_AVAILABLE = False
    print("Warning: live_data module not found. Using synthetic data only.")


@dataclass
class MarketScenario:
    """Complete market scenario for VPP simulation."""
    timestamps: List[datetime]
    solar_kw: List[float]
    load_kw: List[float]
    price_gbp_kwh: List[float]

    # Scenario metadata
    volatility_multiplier: float
    cloud_cover_factor: float
    daily_load_kwh: float
    
    # NEW: Data source tracking
    price_data_source: str = "synthetic"  # "synthetic" or "octopus_agile"
    price_region: str = None


class MarketDataGenerator:
    """
    Generates realistic UK energy market data.

    Creates synthetic but realistic profiles for:
    - Solar PV generation (with cloud intermittency)
    - Household demand (behavioral patterns)
    - Day-ahead electricity prices (duck curve + volatility)
    
    **NEW:** Can fetch REAL UK prices from Octopus Energy Agile API
    """

    def __init__(
        self,
        seed: int = None,
        use_live_prices: bool = False,
        octopus_region: str = 'A'
    ):
        """
        Args:
            seed: Random seed for reproducibility (None = random, 42 = fixed for testing)
            use_live_prices: If True, fetch real UK prices from Octopus API
            octopus_region: UK region code (A-P) for Agile pricing
        """
        # Use None for truly random, or provide a seed for reproducibility
        if seed is None:
            self.seed = np.random.randint(0, 1000000)
        else:
            self.seed = seed

        self.use_live_prices = use_live_prices
        self.octopus_region = octopus_region
        np.random.seed(self.seed)

    def generate_scenario(
        self,
        system_size_kwp: float = 3.5,
        daily_load_kwh: float = 12.0,
        volatility_multiplier: float = 1.0,
        cloud_cover_factor: float = 0.3,
        start_date: datetime = None,
        intervals: int = 96
    ) -> MarketScenario:
        """
        Generate complete 24-hour scenario with optional live price data.

        Args:
            system_size_kwp: Solar system size (kWp)
            daily_load_kwh: Daily consumption (kWh)
            volatility_multiplier: Price volatility (1x = normal, 5x = extreme)
            cloud_cover_factor: Solar intermittency (0 = clear, 1 = cloudy)
            start_date: Scenario start (defaults to today midnight)
            intervals: Number of timesteps (96 = 15-min resolution)

        Returns:
            MarketScenario with all profiles (live or synthetic prices)
        """
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Generate timestamps
        timestamps = [start_date + timedelta(minutes=15*i) for i in range(intervals)]
        hours = np.array([ts.hour + ts.minute/60 for ts in timestamps])

        # Generate solar profile (always synthetic)
        solar_kw = self._generate_solar(
            hours=hours,
            system_size_kwp=system_size_kwp,
            cloud_factor=cloud_cover_factor
        )

        # Generate load profile (always synthetic)
        load_kw = self._generate_load(
            hours=hours,
            daily_kwh=daily_load_kwh
        )

        # Generate or fetch price profile
        price_gbp_kwh = None
        price_source = "synthetic"
        price_region = None
        
        if self.use_live_prices and LIVE_DATA_AVAILABLE:
            # Try to fetch live prices
            print(f"Fetching live prices for region {self.octopus_region}...")
            live_prices = OctopusEnergyAPI.fetch_agile_prices(
                date=start_date,
                region=self.octopus_region,
                hours=24
            )
            
            if live_prices and len(live_prices) >= intervals:
                price_gbp_kwh = live_prices[:intervals]
                price_source = "octopus_agile"
                price_region = self.octopus_region
                print(f"✅ Using live Octopus Agile prices ({self.octopus_region})")
            else:
                print("⚠️  Live prices unavailable, falling back to synthetic")
        
        # Fallback to synthetic prices if needed
        if price_gbp_kwh is None:
            price_gbp_kwh = self._generate_prices(
                hours=hours,
                volatility=volatility_multiplier
            )

        return MarketScenario(
            timestamps=timestamps,
            solar_kw=solar_kw,
            load_kw=load_kw,
            price_gbp_kwh=price_gbp_kwh,
            volatility_multiplier=volatility_multiplier,
            cloud_cover_factor=cloud_cover_factor,
            daily_load_kwh=daily_load_kwh,
            price_data_source=price_source,
            price_region=price_region
        )

    def _generate_solar(
        self,
        hours: np.ndarray,
        system_size_kwp: float,
        cloud_factor: float
    ) -> List[float]:
        """
        Generate solar PV profile with cloud intermittency.

        Uses Gaussian curve peaking at solar noon with:
        - Base curve: Clear-sky irradiance
        - Cloud noise: Random fluctuations
        """
        # Clear-sky profile (Gaussian centered at 12:00)
        peak_capacity_factor = 0.85  # Max output as fraction of rated capacity
        clear_sky = system_size_kwp * peak_capacity_factor * np.exp(-((hours - 12)**2) / (2 * 2.5**2))

        # Add cloud intermittency
        np.random.seed(self.seed)
        noise_std = cloud_factor * 0.3  # 0.3 = aggressive clouds
        cloud_noise = np.random.normal(0, noise_std, len(hours))
        cloud_factor_array = np.clip(1 + cloud_noise, 0.2, 1.0)

        solar = np.maximum(0, clear_sky * cloud_factor_array)
        return solar.tolist()

    def _generate_load(
        self,
        hours: np.ndarray,
        daily_kwh: float
    ) -> List[float]:
        """
        Generate typical UK household load profile.

        Pattern:
        - Morning peak (07:00-09:00): Breakfast, heating
        - Daytime low (10:00-16:00): Out of house
        - Evening peak (17:00-21:00): Cooking, appliances
        - Overnight baseload: Fridge, standby
        """
        # Morning peak
        morning = 1.5 * np.exp(-((hours - 7.5)**2) / (2 * 1.0**2))

        # Evening peak (larger)
        evening = 2.2 * np.exp(-((hours - 19)**2) / (2 * 1.5**2))

        # Baseload
        base = 0.5

        load = base + morning + evening

        # Add random variation (appliance usage)
        np.random.seed(self.seed + 1)
        load += np.random.normal(0, 0.1, len(hours))
        load = np.maximum(0.3, load)

        # Scale to match target daily consumption
        current_daily = np.sum(load) * 0.25  # 15-min intervals
        load = load * (daily_kwh / current_daily)

        return load.tolist()

    def _generate_prices(
        self,
        hours: np.ndarray,
        volatility: float
    ) -> List[float]:
        """
        Generate UK day-ahead electricity prices (GBP/kWh).

        Simulates the "duck curve" phenomenon:
        - Low/negative prices at midday (solar flooding)
        - High prices at evening peak (scarcity)
        - Moderate overnight prices

        Volatility multiplier:
        - 1x = typical market conditions
        - 2-3x = high renewable penetration
        - 4-5x = extreme events (wind lull + cold snap)
        """
        # Base overnight price
        base = 0.05 + 0.01 * np.sin((hours - 3) * np.pi / 12)

        # Solar depression (midday low prices)
        solar_effect = -0.04 * np.exp(-((hours - 13)**2) / (2 * 1.5**2))

        # Evening scarcity spike
        evening_spike = 0.12 * np.exp(-((hours - 18.5)**2) / (2 * 1.0**2))

        # Combine base structure
        price_base = base + solar_effect + evening_spike

        # Add volatility
        np.random.seed(self.seed + 2)
        noise_std = 0.008 * volatility
        volatility_noise = np.random.normal(0, noise_std, len(hours))

        # Add occasional price spikes (extreme events)
        if volatility > 2.0:
            spike_prob = (volatility - 2.0) * 0.05
            spikes = np.random.random(len(hours)) < spike_prob
            spike_magnitude = np.random.uniform(0.1, 0.3, len(hours)) * spikes
            volatility_noise += spike_magnitude

        price = price_base + volatility_noise

        # Floor at 1p/kWh (prevent negative prices in display)
        price = np.maximum(0.01, price)

        return price.tolist()


# Convenience function for testing
def compare_live_vs_synthetic():
    """
    Compare live Octopus prices with synthetic model.
    Useful for calibrating synthetic price generator.
    """
    print("\n" + "="*70)
    print("COMPARING LIVE VS SYNTHETIC PRICES")
    print("="*70)
    
    if not LIVE_DATA_AVAILABLE:
        print("❌ Live data module not available")
        return
    
    # Generate both
    gen_live = MarketDataGenerator(use_live_prices=True, octopus_region='A')
    gen_synthetic = MarketDataGenerator(use_live_prices=False)
    
    scenario_live = gen_live.generate_scenario()
    scenario_synthetic = gen_synthetic.generate_scenario()
    
    import numpy as np
    
    if scenario_live.price_data_source == "octopus_agile":
        live_prices = np.array(scenario_live.price_gbp_kwh)
        synth_prices = np.array(scenario_synthetic.price_gbp_kwh)
        
        print(f"\nLIVE PRICES (Octopus Agile {scenario_live.price_region}):")
        print(f"  Min:  £{np.min(live_prices):.4f}/kWh")
        print(f"  Max:  £{np.max(live_prices):.4f}/kWh")
        print(f"  Mean: £{np.mean(live_prices):.4f}/kWh")
        print(f"  Std:  £{np.std(live_prices):.4f}/kWh")
        
        print(f"\nSYNTHETIC PRICES:")
        print(f"  Min:  £{np.min(synth_prices):.4f}/kWh")
        print(f"  Max:  £{np.max(synth_prices):.4f}/kWh")
        print(f"  Mean: £{np.mean(synth_prices):.4f}/kWh")
        print(f"  Std:  £{np.std(synth_prices):.4f}/kWh")
        
        # Calculate correlation
        correlation = np.corrcoef(live_prices, synth_prices)[0, 1]
        print(f"\nCorrelation: {correlation:.3f}")
        
        if correlation > 0.7:
            print("✅ Synthetic model is well-calibrated")
        elif correlation > 0.5:
            print("⚠️  Synthetic model is reasonably calibrated")
        else:
            print("❌ Synthetic model needs recalibration")
    else:
        print("❌ Could not fetch live prices for comparison")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    # Test both modes
    print("Testing MarketDataGenerator...")
    
    # Test 1: Synthetic
    gen = MarketDataGenerator(use_live_prices=False)
    scenario = gen.generate_scenario()
    print(f"✅ Synthetic scenario generated: {len(scenario.price_gbp_kwh)} prices")
    
    # Test 2: Live (if available)
    if LIVE_DATA_AVAILABLE:
        gen_live = MarketDataGenerator(use_live_prices=True, octopus_region='A')
        scenario_live = gen_live.generate_scenario()
        print(f"✅ Live scenario: {scenario_live.price_data_source}")
        
        # Compare
        compare_live_vs_synthetic()
    else:
        print("⚠️  Live data module not available, skipping live test")
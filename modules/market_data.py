# coding: utf-8
"""
Market Data Generator
=====================
Realistic UK energy market simulation with configurable volatility.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple
from dataclasses import dataclass


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


class MarketDataGenerator:
    """
    Generates realistic UK energy market data.

    Creates synthetic but realistic profiles for:
    - Solar PV generation (with cloud intermittency)
    - Household demand (behavioral patterns)
    - Day-ahead electricity prices (duck curve + volatility)
    """

    def __init__(self, seed: int = 42):
        """
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        np.random.seed(seed)

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
        Generate complete 24-hour scenario.

        Args:
            system_size_kwp: Solar system size (kWp)
            daily_load_kwh: Daily consumption (kWh)
            volatility_multiplier: Price volatility (1x = normal, 5x = extreme)
            cloud_cover_factor: Solar intermittency (0 = clear, 1 = cloudy)
            start_date: Scenario start (defaults to today midnight)
            intervals: Number of timesteps (96 = 15-min resolution)

        Returns:
            MarketScenario with all profiles
        """
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Generate timestamps
        timestamps = [start_date + timedelta(minutes=15*i) for i in range(intervals)]
        hours = np.array([ts.hour + ts.minute/60 for ts in timestamps])

        # Generate solar profile
        solar_kw = self._generate_solar(
            hours=hours,
            system_size_kwp=system_size_kwp,
            cloud_factor=cloud_cover_factor
        )

        # Generate load profile
        load_kw = self._generate_load(
            hours=hours,
            daily_kwh=daily_load_kwh
        )

        # Generate price profile
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
            daily_load_kwh=daily_load_kwh
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
        - Cloud noise: Ornstein-Uhlenbeck process
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

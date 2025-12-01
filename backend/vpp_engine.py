# coding: utf-8
"""
Virtual Power Plant (VPP) Optimization Engine
==============================================
Physics-constrained battery optimization for UK energy markets.

This module provides the core optimization logic for residential
Solar+Battery systems acting as rational economic agents while
respecting grid connection limits (G99 compliance).
"""

import numpy as np
import pandas as pd
from scipy.optimize import linprog
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class VPPOptimizer:
    """
    VPP Optimization Engine using Linear Programming.

    Maximizes revenue through price arbitrage while enforcing:
    - Battery capacity and power constraints
    - Round-trip efficiency losses
    - Grid export limits (prevents transformer overload)
    """

    def __init__(
        self,
        battery_capacity_kwh: float = 13.5,
        battery_power_kw: float = 5.0,
        battery_efficiency: float = 0.90,
        grid_export_limit_kw: float = 4.0,
        timestep_hours: float = 0.25
    ):
        """
        Initialize VPP optimizer.

        Args:
            battery_capacity_kwh: Battery energy capacity (kWh)
            battery_power_kw: Max charge/discharge power (kW)
            battery_efficiency: Round-trip efficiency (0-1)
            grid_export_limit_kw: DNO connection limit (kW)
            timestep_hours: Time resolution (0.25 = 15 min)
        """
        self.battery_capacity = battery_capacity_kwh
        self.battery_power = battery_power_kw
        self.efficiency = battery_efficiency
        self.grid_limit = grid_export_limit_kw
        self.dt = timestep_hours

    def optimize(
        self,
        solar_kw: List[float],
        load_kw: List[float],
        price_gbp_per_kwh: List[float],
        initial_soc_pct: float = 50.0
    ) -> Dict:
        """
        Run constrained optimization to find optimal battery schedule.

        Args:
            solar_kw: Solar generation forecast (kW) per timestep
            load_kw: Load forecast (kW) per timestep
            price_gbp_per_kwh: Electricity price (GBP/kWh) per timestep
            initial_soc_pct: Starting battery charge (%)

        Returns:
            Dictionary with:
                - battery_charge_kw: Charging schedule
                - battery_discharge_kw: Discharging schedule
                - soc_pct: State of charge trajectory
                - grid_export_kw: Net grid power
                - revenue_gbp: Total revenue
                - energy_cost_gbp: Cost of imports
                - net_profit_gbp: Profit after costs
        """
        N = len(solar_kw)
        solar = np.array(solar_kw)
        load = np.array(load_kw)
        price = np.array(price_gbp_per_kwh)

        # Decision variables: [charge_0..N-1, discharge_0..N-1, soc_0..N]
        # Total: 3*N + 1

        # Objective: Maximize revenue = sum(grid_export * price * dt)
        # Grid export = solar - load + discharge - charge
        # Minimize negative revenue
        c = np.zeros(3*N + 1)
        for t in range(N):
            # Charging costs money (reduces revenue)
            c[t] = price[t] * self.dt
            # Discharging earns money (increases revenue)
            c[N + t] = -price[t] * self.dt

        # Inequality constraints: A_ub @ x <= b_ub
        A_ub = []
        b_ub = []

        # Charge power limits
        for t in range(N):
            constraint = np.zeros(3*N + 1)
            constraint[t] = 1
            A_ub.append(constraint)
            b_ub.append(self.battery_power)

        # Discharge power limits
        for t in range(N):
            constraint = np.zeros(3*N + 1)
            constraint[N + t] = 1
            A_ub.append(constraint)
            b_ub.append(self.battery_power)

        # SoC capacity limits
        for t in range(N + 1):
            constraint = np.zeros(3*N + 1)
            constraint[2*N + t] = 1
            A_ub.append(constraint)
            b_ub.append(self.battery_capacity)

        # Grid export limit (THE KEY CONSTRAINT)
        for t in range(N):
            constraint = np.zeros(3*N + 1)
            constraint[N + t] = 1   # discharge
            constraint[t] = -1      # charge
            A_ub.append(constraint)
            b_ub.append(self.grid_limit - (solar[t] - load[t]))

        A_ub = np.array(A_ub)
        b_ub = np.array(b_ub)

        # Equality constraints: A_eq @ x = b_eq
        A_eq = []
        b_eq = []

        # Battery dynamics
        eta_charge = np.sqrt(self.efficiency)
        eta_discharge = np.sqrt(self.efficiency)

        for t in range(N):
            constraint = np.zeros(3*N + 1)
            constraint[2*N + t + 1] = 1  # SoC[t+1]
            constraint[2*N + t] = -1     # SoC[t]
            constraint[t] = -eta_charge * self.dt
            constraint[N + t] = 1/eta_discharge * self.dt
            A_eq.append(constraint)
            b_eq.append(0)

        # Initial SoC
        initial_soc = np.zeros(3*N + 1)
        initial_soc[2*N] = 1
        A_eq.append(initial_soc)
        b_eq.append((initial_soc_pct / 100) * self.battery_capacity)

        A_eq = np.array(A_eq)
        b_eq = np.array(b_eq)

        # Variable bounds
        bounds = [(0, None)] * (2*N) + [(0, None)] * (N + 1)

        # Solve
        result = linprog(
            c=c,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method='highs'
        )

        if not result.success:
            raise RuntimeError(f"Optimization failed: {result.message}")

        # Extract solution
        x = result.x
        charge = x[:N].tolist()
        discharge = x[N:2*N].tolist()
        soc_kwh = x[2*N:2*N+N]
        soc_pct = (soc_kwh / self.battery_capacity * 100).tolist()

        grid_export = (solar - load + np.array(discharge) - np.array(charge)).tolist()

        # Calculate costs
        grid_import = np.maximum(0, -np.array(grid_export))
        grid_export_pos = np.maximum(0, grid_export)

        energy_cost = np.sum(grid_import * price * self.dt)
        revenue = np.sum(grid_export_pos * price * self.dt)
        net_profit = revenue - energy_cost

        return {
            'battery_charge_kw': charge,
            'battery_discharge_kw': discharge,
            'soc_pct': soc_pct,
            'grid_export_kw': grid_export,
            'revenue_gbp': float(revenue),
            'energy_cost_gbp': float(energy_cost),
            'net_profit_gbp': float(net_profit),
            'success': True,
            'message': result.message
        }


def generate_uk_price_profile(start_time: datetime, intervals: int) -> List[float]:
    """
    Generate realistic UK day-ahead price profile (GBP/kWh).

    Simulates the "duck curve" with:
    - Low/negative prices at midday (solar flooding)
    - High prices at evening peak (17:00-20:00)
    - Moderate overnight prices
    """
    hours = np.array([
        (start_time + timedelta(hours=i*0.25)).hour +
        (start_time + timedelta(hours=i*0.25)).minute / 60
        for i in range(intervals)
    ])

    # Base overnight price
    base = 0.05 + 0.01 * np.sin((hours - 3) * np.pi / 12)

    # Solar depression (midday low)
    solar_effect = -0.04 * np.exp(-((hours - 13)**2) / (2 * 1.5**2))

    # Evening peak
    evening_spike = 0.12 * np.exp(-((hours - 18.5)**2) / (2 * 1.0**2))

    # Add volatility
    np.random.seed(42)
    noise = np.random.normal(0, 0.008, len(hours))

    price = base + solar_effect + evening_spike + noise
    price = np.maximum(0.01, price)  # Floor at 1p/kWh

    return price.tolist()


def generate_load_profile(start_time: datetime, intervals: int, daily_kwh: float = 10.0) -> List[float]:
    """
    Generate typical UK household load profile.

    Args:
        start_time: Start datetime
        intervals: Number of 15-min intervals
        daily_kwh: Daily consumption (kWh)
    """
    hours = np.array([
        (start_time + timedelta(hours=i*0.25)).hour +
        (start_time + timedelta(hours=i*0.25)).minute / 60
        for i in range(intervals)
    ])

    # Morning peak (07:00-09:00)
    morning = 1.5 * np.exp(-((hours - 7.5)**2) / (2 * 1.0**2))

    # Evening peak (17:00-21:00)
    evening = 2.2 * np.exp(-((hours - 19)**2) / (2 * 1.5**2))

    # Baseload
    base = 0.5

    load = base + morning + evening

    # Scale to match daily consumption
    current_daily = np.sum(load) * 0.25
    load = load * (daily_kwh / current_daily)

    return load.tolist()


def calculate_grid_impact(
    grid_export_kw: List[float],
    grid_limit_kw: float,
    line_resistance_ohm: float = 0.075
) -> Dict:
    """
    Calculate grid impact metrics including voltage rise.

    Args:
        grid_export_kw: Net grid export per timestep (kW)
        grid_limit_kw: DNO connection limit (kW)
        line_resistance_ohm: LV feeder resistance (Ohm)

    Returns:
        Dictionary with voltage rise and grid stress metrics
    """
    export_pos = np.maximum(0, grid_export_kw)

    # Voltage rise calculation (simplified)
    V_nominal = 230  # UK single-phase
    voltage_rise_V = (export_pos * 1000 * line_resistance_ohm) / V_nominal
    voltage_rise_pct = (voltage_rise_V / V_nominal) * 100

    # Grid stress (0-1 scale)
    grid_stress = np.clip(export_pos / grid_limit_kw, 0, 1)

    return {
        'max_voltage_rise_V': float(np.max(voltage_rise_V)),
        'max_voltage_rise_pct': float(np.max(voltage_rise_pct)),
        'peak_grid_stress': float(np.max(grid_stress)),
        'times_at_limit': int(np.sum(export_pos > grid_limit_kw * 0.95)),
        'g99_compliant': float(np.max(voltage_rise_pct)) < 10.0
    }

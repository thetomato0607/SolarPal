"""
Virtual Power Plant (VPP) API Endpoints
========================================
FastAPI routes for VPP optimization and analysis.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vpp_engine import (
    VPPOptimizer,
    generate_uk_price_profile,
    generate_load_profile,
    calculate_grid_impact
)

router = APIRouter()


@router.post("/optimize")
def optimize_vpp(
    solar_forecast_kw: List[float],
    load_forecast_kw: List[float] = None,
    price_forecast_gbp_kwh: List[float] = None,
    battery_capacity_kwh: float = 13.5,
    battery_power_kw: float = 5.0,
    grid_export_limit_kw: float = 4.0,
    initial_soc_pct: float = 50.0
):
    """
    Optimize battery operation for given forecasts.

    Example request:
    ```json
    {
        "solar_forecast_kw": [0, 0, 0.5, 1.2, 2.3, ...],  // 96 values for 24h
        "battery_capacity_kwh": 13.5,
        "grid_export_limit_kw": 4.0
    }
    ```

    Returns optimal battery schedule and financial metrics.
    """
    try:
        N = len(solar_forecast_kw)

        # Generate default load profile if not provided
        if load_forecast_kw is None:
            load_forecast_kw = generate_load_profile(
                start_time=datetime.now(),
                intervals=N,
                daily_kwh=10.0
            )

        # Generate UK price profile if not provided
        if price_forecast_gbp_kwh is None:
            price_forecast_gbp_kwh = generate_uk_price_profile(
                start_time=datetime.now(),
                intervals=N
            )

        # Validate inputs
        if len(load_forecast_kw) != N or len(price_forecast_gbp_kwh) != N:
            raise HTTPException(
                status_code=400,
                detail="All forecasts must have the same length"
            )

        # Initialize optimizer
        optimizer = VPPOptimizer(
            battery_capacity_kwh=battery_capacity_kwh,
            battery_power_kw=battery_power_kw,
            battery_efficiency=0.90,
            grid_export_limit_kw=grid_export_limit_kw,
            timestep_hours=0.25
        )

        # Run optimization
        result = optimizer.optimize(
            solar_kw=solar_forecast_kw,
            load_kw=load_forecast_kw,
            price_gbp_per_kwh=price_forecast_gbp_kwh,
            initial_soc_pct=initial_soc_pct
        )

        # Calculate grid impact
        grid_impact = calculate_grid_impact(
            grid_export_kw=result['grid_export_kw'],
            grid_limit_kw=grid_export_limit_kw
        )

        # Return combined result
        return {
            "optimization": result,
            "grid_impact": grid_impact,
            "inputs": {
                "intervals": N,
                "battery_kwh": battery_capacity_kwh,
                "battery_kw": battery_power_kw,
                "grid_limit_kw": grid_export_limit_kw
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulate")
def simulate_vpp_day(
    system_size_kwp: float = 3.0,
    daily_load_kwh: float = 10.0,
    battery_capacity_kwh: float = 13.5,
    grid_export_limit_kw: float = 4.0,
    include_charts: bool = False
):
    """
    Run a full 24-hour VPP simulation with synthetic data.

    This endpoint generates realistic solar, load, and price profiles
    then optimizes battery operation.

    Example: GET /vpp/simulate?system_size_kwp=4.0&daily_load_kwh=12

    Returns:
        Complete simulation results with optimization and grid analysis
    """
    try:
        # Generate synthetic solar profile (96 intervals = 24h @ 15min)
        start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        N = 96

        # Solar generation (Gaussian curve peaking at noon)
        hours = [(start_time + timedelta(hours=i*0.25)).hour +
                (start_time + timedelta(hours=i*0.25)).minute / 60
                for i in range(N)]

        import numpy as np
        solar_base = system_size_kwp * 0.85 * np.exp(-((np.array(hours) - 12)**2) / (2 * 2.5**2))
        np.random.seed(42)
        cloud_factor = np.clip(1 + np.random.normal(0, 0.2, N), 0.3, 1.0)
        solar_kw = (np.maximum(0, solar_base) * cloud_factor).tolist()

        # Generate load and price profiles
        load_kw = generate_load_profile(start_time, N, daily_load_kwh)
        price_gbp_kwh = generate_uk_price_profile(start_time, N)

        # Run optimization
        optimizer = VPPOptimizer(
            battery_capacity_kwh=battery_capacity_kwh,
            battery_power_kw=5.0,
            battery_efficiency=0.90,
            grid_export_limit_kw=grid_export_limit_kw
        )

        result = optimizer.optimize(
            solar_kw=solar_kw,
            load_kw=load_kw,
            price_gbp_per_kwh=price_gbp_kwh,
            initial_soc_pct=50.0
        )

        # Grid impact
        grid_impact = calculate_grid_impact(
            grid_export_kw=result['grid_export_kw'],
            grid_limit_kw=grid_export_limit_kw
        )

        # Compile response
        response = {
            "simulation_date": start_time.isoformat(),
            "inputs": {
                "system_size_kwp": system_size_kwp,
                "daily_load_kwh": daily_load_kwh,
                "battery_capacity_kwh": battery_capacity_kwh,
                "grid_export_limit_kw": grid_export_limit_kw
            },
            "forecasts": {
                "solar_kw": solar_kw,
                "load_kw": load_kw,
                "price_gbp_kwh": price_gbp_kwh
            },
            "optimization": result,
            "grid_impact": grid_impact,
            "summary": {
                "daily_revenue_gbp": result['revenue_gbp'],
                "daily_cost_gbp": result['energy_cost_gbp'],
                "net_profit_gbp": result['net_profit_gbp'],
                "battery_cycles": sum(result['battery_discharge_kw']) * 0.25 / battery_capacity_kwh,
                "max_grid_export_kw": max(result['grid_export_kw']),
                "grid_compliant": grid_impact['g99_compliant']
            }
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark")
def benchmark_vpp(
    system_size_kwp: float = 3.0,
    battery_capacity_kwh: float = 13.5
):
    """
    Compare VPP optimization vs. baseline (no battery).

    Shows the economic value of the battery system.

    Example: GET /vpp/benchmark?system_size_kwp=4.0&battery_capacity_kwh=10.0

    Returns:
        Comparison of scenarios with financial impact
    """
    try:
        import numpy as np
        start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        N = 96

        # Generate profiles
        hours = [(start_time + timedelta(hours=i*0.25)).hour +
                (start_time + timedelta(hours=i*0.25)).minute / 60
                for i in range(N)]

        solar_base = system_size_kwp * 0.85 * np.exp(-((np.array(hours) - 12)**2) / (2 * 2.5**2))
        np.random.seed(42)
        solar_kw = np.maximum(0, solar_base * np.clip(1 + np.random.normal(0, 0.2, N), 0.3, 1.0))

        load_kw = np.array(generate_load_profile(start_time, N, 10.0))
        price_gbp_kwh = np.array(generate_uk_price_profile(start_time, N))

        # Scenario 1: No battery (baseline)
        grid_no_battery = solar_kw - load_kw
        import_no_battery = np.maximum(0, -grid_no_battery)
        export_no_battery = np.maximum(0, grid_no_battery)

        cost_no_battery = np.sum(import_no_battery * price_gbp_kwh * 0.25)
        revenue_no_battery = np.sum(export_no_battery * price_gbp_kwh * 0.5 * 0.25)  # 50% export tariff
        net_no_battery = revenue_no_battery - cost_no_battery

        # Scenario 2: With VPP optimization
        optimizer = VPPOptimizer(
            battery_capacity_kwh=battery_capacity_kwh,
            battery_power_kw=5.0,
            battery_efficiency=0.90,
            grid_export_limit_kw=4.0
        )

        result = optimizer.optimize(
            solar_kw=solar_kw.tolist(),
            load_kw=load_kw.tolist(),
            price_gbp_per_kwh=price_gbp_kwh.tolist(),
            initial_soc_pct=50.0
        )

        # Calculate savings
        net_with_vpp = result['net_profit_gbp']
        daily_benefit = net_with_vpp - net_no_battery
        annual_benefit = daily_benefit * 365

        # ROI calculation (assuming battery costs £7000)
        battery_cost_gbp = 7000
        payback_years = battery_cost_gbp / annual_benefit if annual_benefit > 0 else float('inf')

        return {
            "baseline_no_battery": {
                "daily_cost_gbp": float(cost_no_battery),
                "daily_revenue_gbp": float(revenue_no_battery),
                "net_daily_gbp": float(net_no_battery)
            },
            "with_vpp_optimization": {
                "daily_cost_gbp": result['energy_cost_gbp'],
                "daily_revenue_gbp": result['revenue_gbp'],
                "net_daily_gbp": result['net_profit_gbp']
            },
            "benefit_analysis": {
                "daily_saving_gbp": float(daily_benefit),
                "annual_saving_gbp": float(annual_benefit),
                "battery_cost_gbp": battery_cost_gbp,
                "payback_years": float(payback_years),
                "roi_percent": float((annual_benefit / battery_cost_gbp) * 100) if battery_cost_gbp > 0 else 0
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def vpp_health():
    """Health check for VPP service."""
    return {
        "status": "operational",
        "service": "Virtual Power Plant Optimizer",
        "version": "1.0.0"
    }

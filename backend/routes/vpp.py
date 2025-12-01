"""
Virtual Power Plant (VPP) API Endpoints
========================================
FastAPI routes for VPP optimization and analysis.
"""

from fastapi import APIRouter, HTTPException
from typing import List
import sys
import os

# Add project root to path for imports (single source of truth)
# This file is in backend/routes/, so go up 2 levels to reach project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import from modules/ (consolidated optimization logic)
from modules.optimization import BatteryOptimizer, BatteryAsset
from modules.market_data import MarketDataGenerator
from modules.grid_physics import GridConstraintChecker

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

        # Generate default load/price profiles if not provided
        market_gen = MarketDataGenerator()

        if load_forecast_kw is None:
            scenario = market_gen.generate_scenario(
                system_size_kwp=1.0,
                daily_load_kwh=10.0,
                intervals=N
            )
            load_forecast_kw = scenario.load_kw

        if price_forecast_gbp_kwh is None:
            scenario = market_gen.generate_scenario(
                system_size_kwp=1.0,
                daily_load_kwh=10.0,
                intervals=N
            )
            price_forecast_gbp_kwh = scenario.price_gbp_kwh

        # Validate inputs
        if len(load_forecast_kw) != N or len(price_forecast_gbp_kwh) != N:
            raise HTTPException(
                status_code=400,
                detail="All forecasts must have the same length"
            )

        # Initialize optimizer (single source of truth)
        optimizer = BatteryOptimizer(timestep_minutes=15)
        asset = BatteryAsset(
            capacity_kwh=battery_capacity_kwh,
            power_kw=battery_power_kw,
            efficiency=0.90,
            initial_soc_pct=initial_soc_pct
        )

        # Run optimization with degradation cost
        result = optimizer.optimize(
            asset=asset,
            solar_kw=solar_forecast_kw,
            load_kw=load_forecast_kw,
            price_gbp_kwh=price_forecast_gbp_kwh,
            grid_export_limit_kw=grid_export_limit_kw
        )

        # Calculate grid impact
        grid_checker = GridConstraintChecker(grid_export_limit_kw=grid_export_limit_kw)
        grid_impact = grid_checker.check_violations(result.grid_export_kw)

        # Return combined result (convert dataclass to dict)
        return {
            "optimization": {
                "charge_schedule_kw": result.charge_schedule_kw,
                "discharge_schedule_kw": result.discharge_schedule_kw,
                "soc_trajectory_pct": result.soc_trajectory_pct,
                "grid_export_kw": result.grid_export_kw,
                "revenue_gbp": result.revenue_gbp,
                "cost_gbp": result.cost_gbp,
                "net_profit_gbp": result.net_profit_gbp,
                "sharpe_ratio": result.sharpe_ratio,
                "solver_status": result.solver_status,
                "solve_time_ms": result.solve_time_ms
            },
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
    battery_power_kw: float = 5.0,
    grid_export_limit_kw: float = 4.0,
    initial_soc_pct: float = 50.0,
    volatility_multiplier: float = 1.0,
    cloud_cover_factor: float = 0.3
):
    """
    Run a full 24-hour VPP simulation with synthetic data.

    This endpoint generates realistic solar, load, and price profiles
    then optimizes battery operation using the DRY-compliant modules.

    Example: GET /vpp/simulate?system_size_kwp=4.0&daily_load_kwh=12

    Returns:
        Complete simulation results with optimization and grid analysis
    """
    try:
        # Generate market scenario using consolidated module
        market_gen = MarketDataGenerator()
        scenario = market_gen.generate_scenario(
            system_size_kwp=system_size_kwp,
            daily_load_kwh=daily_load_kwh,
            volatility_multiplier=volatility_multiplier,
            cloud_cover_factor=cloud_cover_factor,
            intervals=96
        )

        # Create battery asset
        asset = BatteryAsset(
            capacity_kwh=battery_capacity_kwh,
            power_kw=battery_power_kw,
            efficiency=0.90,
            initial_soc_pct=initial_soc_pct
        )

        # Run optimization (single source of truth)
        optimizer = BatteryOptimizer(timestep_minutes=15)
        result = optimizer.optimize(
            asset=asset,
            solar_kw=scenario.solar_kw,
            load_kw=scenario.load_kw,
            price_gbp_kwh=scenario.price_gbp_kwh,
            grid_export_limit_kw=grid_export_limit_kw
        )

        # Calculate grid impact
        grid_checker = GridConstraintChecker(grid_export_limit_kw=grid_export_limit_kw)
        grid_impact = grid_checker.check_violations(result.grid_export_kw)

        # Compile response
        return {
            "simulation_date": scenario.timestamps[0].isoformat(),
            "inputs": {
                "system_size_kwp": system_size_kwp,
                "daily_load_kwh": daily_load_kwh,
                "battery_capacity_kwh": battery_capacity_kwh,
                "battery_power_kw": battery_power_kw,
                "grid_export_limit_kw": grid_export_limit_kw,
                "volatility_multiplier": volatility_multiplier,
                "cloud_cover_factor": cloud_cover_factor
            },
            "forecasts": {
                "solar_kw": scenario.solar_kw,
                "load_kw": scenario.load_kw,
                "price_gbp_kwh": scenario.price_gbp_kwh
            },
            "optimization": {
                "charge_schedule_kw": result.charge_schedule_kw,
                "discharge_schedule_kw": result.discharge_schedule_kw,
                "soc_trajectory_pct": result.soc_trajectory_pct,
                "grid_export_kw": result.grid_export_kw,
                "revenue_gbp": result.revenue_gbp,
                "cost_gbp": result.cost_gbp,
                "net_profit_gbp": result.net_profit_gbp,
                "sharpe_ratio": result.sharpe_ratio,
                "utilization_factor": result.utilization_factor,
                "solver_status": result.solver_status,
                "solve_time_ms": result.solve_time_ms
            },
            "grid_impact": grid_impact,
            "summary": {
                "daily_revenue_gbp": result.revenue_gbp,
                "daily_cost_gbp": result.cost_gbp,
                "net_profit_gbp": result.net_profit_gbp,
                "battery_cycles": result.utilization_factor,
                "max_grid_export_kw": max(result.grid_export_kw),
                "grid_compliant": grid_impact['g99_compliant']
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark")
def benchmark_vpp(
    system_size_kwp: float = 3.0,
    battery_capacity_kwh: float = 13.5,
    battery_power_kw: float = 5.0,
    daily_load_kwh: float = 10.0,
    grid_export_limit_kw: float = 4.0
):
    """
    Compare VPP optimization vs. baseline (no battery).

    Shows the economic value of the battery system using the
    consolidated module architecture.

    Example: GET /vpp/benchmark?system_size_kwp=4.0&battery_capacity_kwh=10.0

    Returns:
        Comparison of scenarios with financial impact
    """
    try:
        # Generate market scenario
        market_gen = MarketDataGenerator()
        scenario = market_gen.generate_scenario(
            system_size_kwp=system_size_kwp,
            daily_load_kwh=daily_load_kwh,
            volatility_multiplier=1.0,
            cloud_cover_factor=0.3,
            intervals=96
        )

        # Import calculate_baseline_cost from optimization module
        from modules.optimization import calculate_baseline_cost

        # Scenario 1: No battery (baseline)
        baseline = calculate_baseline_cost(
            solar_kw=scenario.solar_kw,
            load_kw=scenario.load_kw,
            price_gbp_kwh=scenario.price_gbp_kwh
        )

        # Scenario 2: With VPP optimization
        asset = BatteryAsset(
            capacity_kwh=battery_capacity_kwh,
            power_kw=battery_power_kw,
            efficiency=0.90,
            initial_soc_pct=50.0
        )

        optimizer = BatteryOptimizer(timestep_minutes=15)
        result = optimizer.optimize(
            asset=asset,
            solar_kw=scenario.solar_kw,
            load_kw=scenario.load_kw,
            price_gbp_kwh=scenario.price_gbp_kwh,
            grid_export_limit_kw=grid_export_limit_kw
        )

        # Calculate savings
        net_with_vpp = result.net_profit_gbp
        net_no_battery = baseline['net_gbp']
        daily_benefit = net_with_vpp - net_no_battery
        annual_benefit = daily_benefit * 365

        # ROI calculation (Tesla Powerwall cost)
        battery_cost_gbp = 7000
        payback_years = battery_cost_gbp / annual_benefit if annual_benefit > 0 else float('inf')

        return {
            "baseline_no_battery": {
                "daily_cost_gbp": baseline['cost_gbp'],
                "daily_revenue_gbp": baseline['revenue_gbp'],
                "net_daily_gbp": baseline['net_gbp']
            },
            "with_vpp_optimization": {
                "daily_cost_gbp": result.cost_gbp,
                "daily_revenue_gbp": result.revenue_gbp,
                "net_daily_gbp": result.net_profit_gbp
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

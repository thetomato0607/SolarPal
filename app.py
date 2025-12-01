# coding: utf-8
"""
VPP TRADING TERMINAL
====================
Professional energy arbitrage simulation platform.

Bloomberg-style dashboard for grid-connected battery optimization.
"""

import streamlit as st
import numpy as np
from modules.optimization import BatteryOptimizer, BatteryAsset, calculate_baseline_cost
from modules.grid_physics import GridConstraintChecker
from modules.market_data import MarketDataGenerator
from modules.visualization import create_price_chart, create_grid_flow_chart

# Page configuration
st.set_page_config(
    page_title="VPP Trading Terminal",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    /* Force dark theme */
    .stApp {
        background-color: #0E1117;
    }

    /* Header styling */
    h1 {
        color: #00D9FF !important;
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: bold !important;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #262730;
    }

    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR: SCENARIO CONTROLS
# ============================================================================

st.sidebar.markdown("## SCENARIO CONFIGURATION")
st.sidebar.markdown("---")

st.sidebar.markdown("### ASSET PARAMETERS")
battery_capacity = st.sidebar.slider(
    "Battery Capacity (kWh)",
    min_value=5.0,
    max_value=20.0,
    value=13.5,
    step=0.5,
    help="Total energy storage capacity"
)

battery_power = st.sidebar.slider(
    "Inverter Limit (kW)",
    min_value=2.0,
    max_value=10.0,
    value=5.0,
    step=0.5,
    help="Maximum charge/discharge rate"
)

grid_limit = st.sidebar.slider(
    "Grid Export Limit (kW)",
    min_value=2.0,
    max_value=8.0,
    value=4.0,
    step=0.5,
    help="DNO G99 connection limit"
)

initial_soc = st.sidebar.slider(
    "Initial SoC (%)",
    min_value=0,
    max_value=100,
    value=50,
    step=5
)

st.sidebar.markdown("---")
st.sidebar.markdown("### MARKET PARAMETERS")

system_size = st.sidebar.slider(
    "Solar System Size (kWp)",
    min_value=1.0,
    max_value=10.0,
    value=3.5,
    step=0.5
)

volatility = st.sidebar.slider(
    "Price Volatility Multiplier",
    min_value=1.0,
    max_value=5.0,
    value=1.5,
    step=0.5,
    help="1x = normal, 5x = extreme market conditions"
)

cloud_cover = st.sidebar.slider(
    "Solar Irradiance Noise",
    min_value=0.0,
    max_value=1.0,
    value=0.3,
    step=0.1,
    help="0 = clear sky, 1 = heavy clouds"
)

daily_load = st.sidebar.slider(
    "Daily Load (kWh)",
    min_value=5.0,
    max_value=30.0,
    value=12.0,
    step=1.0
)

st.sidebar.markdown("---")
run_simulation = st.sidebar.button("RUN OPTIMIZATION", type="primary", use_container_width=True)

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

# Header
st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <h1>VPP TRADING TERMINAL</h1>
    <p style='color: #888; font-size: 14px; letter-spacing: 1px;'>
        VIRTUAL POWER PLANT | GRID-CONSTRAINED BATTERY ARBITRAGE
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIMULATION ENGINE
# ============================================================================

if run_simulation or 'result' not in st.session_state:
    with st.spinner("Running optimization engine..."):
        # Generate market scenario
        market_gen = MarketDataGenerator()
        scenario = market_gen.generate_scenario(
            system_size_kwp=system_size,
            daily_load_kwh=daily_load,
            volatility_multiplier=volatility,
            cloud_cover_factor=cloud_cover
        )

        # Run optimization
        asset = BatteryAsset(
            capacity_kwh=battery_capacity,
            power_kw=battery_power,
            efficiency=0.90,
            initial_soc_pct=initial_soc
        )

        optimizer = BatteryOptimizer(timestep_minutes=15)
        result = optimizer.optimize(
            asset=asset,
            solar_kw=scenario.solar_kw,
            load_kw=scenario.load_kw,
            price_gbp_kwh=scenario.price_gbp_kwh,
            grid_export_limit_kw=grid_limit
        )

        # Check grid violations
        grid_checker = GridConstraintChecker(grid_export_limit_kw=grid_limit)
        grid_analysis = grid_checker.check_violations(result.grid_export_kw)

        # Calculate baseline (no battery)
        baseline = calculate_baseline_cost(
            solar_kw=scenario.solar_kw,
            load_kw=scenario.load_kw,
            price_gbp_kwh=scenario.price_gbp_kwh
        )

        # Store in session state
        st.session_state.result = result
        st.session_state.scenario = scenario
        st.session_state.grid_analysis = grid_analysis
        st.session_state.baseline = baseline
        st.session_state.asset = asset

# ============================================================================
# METRICS DASHBOARD (Bloomberg-style)
# ============================================================================

if 'result' in st.session_state:
    result = st.session_state.result
    scenario = st.session_state.scenario
    grid_analysis = st.session_state.grid_analysis
    baseline = st.session_state.baseline
    asset = st.session_state.asset

    st.markdown("### PERFORMANCE METRICS")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="NET PROFIT",
            value=f"£{result.net_profit_gbp:.2f}",
            delta=f"vs. baseline: +£{result.net_profit_gbp - baseline['net_gbp']:.2f}",
            delta_color="normal"
        )

    with col2:
        annual_profit = result.net_profit_gbp * 365
        battery_cost = 7000  # Typical Tesla Powerwall
        payback = battery_cost / annual_profit if annual_profit > 0 else 999
        st.metric(
            label="PAYBACK PERIOD",
            value=f"{payback:.1f} years",
            delta=f"ROI: {(annual_profit/battery_cost*100):.1f}%" if payback < 50 else "N/A"
        )

    with col3:
        st.metric(
            label="SHARPE RATIO",
            value=f"{result.sharpe_ratio:.2f}",
            delta="Risk-adjusted return"
        )

    with col4:
        violation_status = "COMPLIANT" if grid_analysis['violation_count'] == 0 else f"{grid_analysis['violation_count']} VIOLATIONS"
        st.metric(
            label="GRID COMPLIANCE",
            value=violation_status,
            delta=f"Max stress: {grid_analysis['peak_grid_stress']*100:.0f}%"
        )

    with col5:
        st.metric(
            label="BATTERY UTILIZATION",
            value=f"{result.utilization_factor*100:.1f}%",
            delta=f"Cycles: {result.utilization_factor:.2f}"
        )

    st.markdown("---")

    # ========================================================================
    # CHART 1: FINANCIAL OPTIMIZATION
    # ========================================================================

    st.markdown("### MARKET ENGINE: Price Arbitrage")

    hours = [ts.hour + ts.minute/60 for ts in scenario.timestamps]

    price_chart = create_price_chart(
        hours=hours,
        price_gbp_kwh=scenario.price_gbp_kwh,
        charge_kw=result.charge_schedule_kw,
        discharge_kw=result.discharge_schedule_kw,
        soc_pct=result.soc_trajectory_pct
    )

    st.plotly_chart(price_chart, use_container_width=True)

    # ========================================================================
    # CHART 2: GRID CONSTRAINT ENFORCEMENT
    # ========================================================================

    st.markdown("### GRID ENGINE: Physical Constraints")

    grid_chart = create_grid_flow_chart(
        hours=hours,
        grid_export_kw=result.grid_export_kw,
        grid_limit_kw=grid_limit
    )

    st.plotly_chart(grid_chart, use_container_width=True)

    # ========================================================================
    # DETAILED ANALYSIS
    # ========================================================================

    st.markdown("---")
    st.markdown("### DETAILED BREAKDOWN")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Financial Summary")
        st.markdown(f"""
        | Metric | Value |
        |--------|-------|
        | **Revenue (Export)** | £{result.revenue_gbp:.2f} |
        | **Cost (Import)** | £{result.cost_gbp:.2f} |
        | **Net Profit** | £{result.net_profit_gbp:.2f} |
        | **Baseline (No Battery)** | £{baseline['net_gbp']:.2f} |
        | **Battery Benefit** | £{result.net_profit_gbp - baseline['net_gbp']:.2f} |
        | **Annual Projection** | £{result.net_profit_gbp * 365:.0f} |
        """)

    with col2:
        st.markdown("#### Grid Impact")
        st.markdown(f"""
        | Metric | Value |
        |--------|-------|
        | **Max Voltage Rise** | {grid_analysis['max_voltage_rise_pct']:.2f}% |
        | **Peak Grid Stress** | {grid_analysis['peak_grid_stress']*100:.0f}% |
        | **Times at Limit** | {grid_analysis['times_at_limit']} intervals |
        | **G99 Compliant** | {'YES' if grid_analysis['g99_compliant'] else 'NO'} |
        | **Violations** | {grid_analysis['violation_count']} |
        """)

    # ========================================================================
    # SOLVER INFO
    # ========================================================================

    with st.expander("Optimization Details"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Solver Status", result.solver_status)
        with col2:
            st.metric("Solve Time", f"{result.solve_time_ms:.1f} ms")
        with col3:
            st.metric("Variables", f"{len(scenario.solar_kw) * 3 + 1}")

        st.markdown(f"""
        **Configuration:**
        - Battery: {asset.capacity_kwh} kWh @ {asset.power_kw} kW ({asset.efficiency*100:.0f}% efficiency)
        - Grid Limit: {grid_limit} kW
        - Timesteps: {len(scenario.solar_kw)} (15-min resolution)
        - Market Volatility: {scenario.volatility_multiplier}x
        - Solar Intermittency: {scenario.cloud_cover_factor*100:.0f}% cloud cover
        """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #555; font-size: 12px; padding: 20px 0;'>
    <p>VPP Trading Terminal v2.0 | Linear Programming Optimization Engine</p>
    <p>Built with Streamlit + SciPy + Plotly | For quant traders and grid engineers</p>
</div>
""", unsafe_allow_html=True)

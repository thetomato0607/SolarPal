"""
VPP Trading Terminal - Core Modules
====================================
Professional-grade energy trading simulation engines.
"""

from .optimization import BatteryOptimizer
from .grid_physics import GridConstraintChecker
from .market_data import MarketDataGenerator
from .visualization import create_price_chart, create_grid_flow_chart

__all__ = [
    'BatteryOptimizer',
    'GridConstraintChecker',
    'MarketDataGenerator',
    'create_price_chart',
    'create_grid_flow_chart'
]

__version__ = '2.0.0'
__author__ = 'SolarPal Quant Team'

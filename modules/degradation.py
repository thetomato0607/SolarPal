import numpy as np
from typing import List

class BatteryDegradationModel:
    """
    Model battery degradation based on Tesla Powerwall warranty.
    
    Tesla guarantees:
    - 70% capacity after 10 years
    - Assumes ~3,650 cycles over lifetime
    - Warranty value: £7,000 × 30% = £2,100 degradation cost
    
    Cost per cycle: £2,100 / 3,650 = £0.58/cycle
    Cost per kWh: £0.58 / 13.5 kWh = £0.043/kWh
    
    BUT: Depth-of-discharge matters (non-linear)
    - 100% DoD: 1.0x wear
    - 50% DoD: 0.5x wear
    - 25% DoD: 0.15x wear (quadratic relationship)
    """
    
    def __init__(
        self,
        battery_capacity_kwh: float = 13.5,
        warranty_cycles: int = 3650,
        replacement_cost_gbp: float = 7000,
        capacity_retention_pct: float = 70
    ):
        self.capacity = battery_capacity_kwh
        self.warranty_cycles = warranty_cycles
        self.replacement_cost = replacement_cost_gbp
        self.retention = capacity_retention_pct / 100
        
        # Calculate degradation cost per full cycle
        degradation_value = replacement_cost_gbp * (1 - self.retention)
        self.cost_per_cycle = degradation_value / warranty_cycles
        
    def calculate_degradation_cost(
        self,
        discharge_kw: List[float],
        timestep_hours: float = 0.25
    ) -> float:
        """
        Calculate total degradation cost for a schedule.
        
        Uses square of discharge depth to model non-linear wear:
            Cost = Σ[(discharge / capacity)² × cost_per_cycle]
        
        This penalizes deep cycles much more than shallow cycles.
        """
        discharge_kwh = np.array(discharge_kw) * timestep_hours
        depth_of_discharge = discharge_kwh / self.capacity
        
        # Quadratic penalty (deep cycles wear faster)
        cycle_equivalent = np.sum(depth_of_discharge ** 2)
        
        degradation_cost = cycle_equivalent * self.cost_per_cycle
        
        return float(degradation_cost)
    
    def calculate_cycle_count(
        self,
        discharge_kw: List[float],
        timestep_hours: float = 0.25
    ) -> float:
        """Calculate equivalent full cycles."""
        total_discharge_kwh = np.sum(discharge_kw) * timestep_hours
        cycles = total_discharge_kwh / self.capacity
        return float(cycles)
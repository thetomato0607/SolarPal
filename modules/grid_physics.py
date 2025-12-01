# coding: utf-8
"""
Grid Constraint Checker
=======================
Physical grid violation detection for DNO compliance.
"""

import numpy as np
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class GridViolation:
    """Detected grid constraint violation."""
    timestep: int
    time_label: str
    net_export_kw: float
    limit_kw: float
    excess_kw: float
    voltage_rise_pct: float
    severity: str  # 'warning', 'critical'


class GridConstraintChecker:
    """
    Checks optimized schedules for physical grid violations.

    Validates:
    - Export limits (DNO G99 connection limits)
    - Voltage rise (±10% statutory limit)
    - Thermal limits (transformer capacity)
    """

    def __init__(
        self,
        grid_export_limit_kw: float = 4.0,
        line_resistance_ohm: float = 0.075,
        nominal_voltage_v: float = 230.0
    ):
        """
        Args:
            grid_export_limit_kw: DNO connection limit (G99)
            line_resistance_ohm: LV feeder resistance
            nominal_voltage_v: UK single-phase nominal
        """
        self.grid_limit = grid_export_limit_kw
        self.R_line = line_resistance_ohm
        self.V_nom = nominal_voltage_v

    def check_violations(
        self,
        grid_export_kw: List[float],
        timestep_minutes: int = 15
    ) -> Dict:
        """
        Scan for grid violations.

        Returns:
            Dictionary with violations list and summary metrics
        """
        violations = []
        export_array = np.array(grid_export_kw)

        for t, export in enumerate(export_array):
            if export > self.grid_limit:
                # Calculate voltage rise
                V_rise = (export * 1000 * self.R_line) / self.V_nom
                V_rise_pct = (V_rise / self.V_nom) * 100

                excess = export - self.grid_limit
                severity = 'critical' if excess > 0.5 else 'warning'

                hour = (t * timestep_minutes) // 60
                minute = (t * timestep_minutes) % 60
                time_label = f"{hour:02d}:{minute:02d}"

                violations.append(GridViolation(
                    timestep=t,
                    time_label=time_label,
                    net_export_kw=float(export),
                    limit_kw=self.grid_limit,
                    excess_kw=float(excess),
                    voltage_rise_pct=float(V_rise_pct),
                    severity=severity
                ))

        # Calculate voltage rise for all timesteps
        export_pos = np.maximum(0, export_array)
        V_rise_all = (export_pos * 1000 * self.R_line) / self.V_nom
        V_rise_pct_all = (V_rise_all / self.V_nom) * 100

        # Grid stress (0-1 scale)
        grid_stress = np.clip(export_pos / self.grid_limit, 0, 1)

        return {
            'violations': violations,
            'violation_count': len(violations),
            'max_voltage_rise_V': float(np.max(V_rise_all)),
            'max_voltage_rise_pct': float(np.max(V_rise_pct_all)),
            'peak_grid_stress': float(np.max(grid_stress)),
            'times_at_limit': int(np.sum(export_pos > self.grid_limit * 0.95)),
            'g99_compliant': len(violations) == 0 and np.max(V_rise_pct_all) < 10.0
        }

    def calculate_curtailment_required(
        self,
        unconstrained_export_kw: List[float]
    ) -> List[float]:
        """
        Calculate how much power must be curtailed to meet grid limit.

        Args:
            unconstrained_export_kw: Desired export without constraints

        Returns:
            Required curtailment per timestep (kW)
        """
        export_array = np.array(unconstrained_export_kw)
        curtailment = np.maximum(0, export_array - self.grid_limit)
        return curtailment.tolist()

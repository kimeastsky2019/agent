"""Energy allocation heuristics for the orchestration layer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from .config import GridConnection, OptimizationParameters


@dataclass
class EnergyDispatch:
    """Represents a single transfer between two regions."""

    source: str
    target: str
    transfer_mw: float
    loss_mw: float


@dataclass
class EnergyDispatchPlan:
    """Aggregated dispatch plan for a network cycle."""

    dispatches: List[EnergyDispatch]

    @property
    def total_transferred(self) -> float:
        return sum(dispatch.transfer_mw for dispatch in self.dispatches)

    @property
    def total_losses(self) -> float:
        return sum(dispatch.loss_mw for dispatch in self.dispatches)


class EnergyAllocationOptimizer:
    """Optimises energy transfers using a deterministic heuristic."""

    def __init__(self, params: OptimizationParameters) -> None:
        self.params = params

    def optimise(
        self,
        region_supply: Dict[str, float],
        region_demand: Dict[str, float],
        connections: Dict[str, Iterable[GridConnection]],
    ) -> EnergyDispatchPlan:
        """Compute a dispatch plan balancing demand deficits."""

        dispatches: List[EnergyDispatch] = []
        surplus_regions = {}
        for region, supply in region_supply.items():
            demand = region_demand.get(region, 0.0)
            surplus_regions[region] = max(
                0.0, supply - demand * (1 + self.params.reserve_margin_fraction)
            )

        deficits = {
            region: max(0.0, demand - region_supply.get(region, 0.0))
            for region, demand in region_demand.items()
        }

        for target, deficit in sorted(deficits.items(), key=lambda item: item[1], reverse=True):
            if deficit <= 0:
                continue
            for connection in connections.get(target, []):
                available = surplus_regions.get(connection.target_region, 0.0)
                if available <= 0:
                    continue
                max_transfer = min(
                    available,
                    self.params.max_transfer_fraction * region_supply.get(connection.target_region, 0.0),
                    deficit,
                    self.params.ramp_limit_mw,
                    connection.capacity_mw,
                )
                if max_transfer <= 0:
                    continue
                effective_transfer = max_transfer * (1 - connection.loss_factor)
                dispatches.append(
                    EnergyDispatch(
                        source=connection.target_region,
                        target=target,
                        transfer_mw=effective_transfer,
                        loss_mw=max_transfer - effective_transfer,
                    )
                )
                surplus_regions[connection.target_region] = max(0.0, available - max_transfer)
                deficit = max(0.0, deficit - effective_transfer)
                if deficit <= 0:
                    break
        return EnergyDispatchPlan(dispatches=dispatches)

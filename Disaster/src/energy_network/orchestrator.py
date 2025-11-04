"""Core orchestration logic for the cross-border energy network."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .config import GridConnection, RegionConfig
from .data_ingestion import DisasterEvent, EnergyStatus
from .forecasting import DemandForecaster, SupplyForecaster
from .optimization import EnergyAllocationOptimizer, EnergyDispatchPlan


@dataclass
class RegionalSnapshot:
    """Operational view of a single region for an orchestration cycle."""

    config: RegionConfig
    energy_status: EnergyStatus
    disaster_event: DisasterEvent


class EnergyOrchestrator:
    """Coordinates forecasting and optimisation for the energy network."""

    def __init__(
        self,
        region_configs: Dict[str, RegionConfig],
        optimizer: EnergyAllocationOptimizer,
        demand_forecaster: DemandForecaster | None = None,
        supply_forecaster: SupplyForecaster | None = None,
    ) -> None:
        self.region_configs = region_configs
        self.optimizer = optimizer
        self.demand_forecaster = demand_forecaster or DemandForecaster()
        self.supply_forecaster = supply_forecaster or SupplyForecaster()

    def _forecast_region(self, snapshot: RegionalSnapshot) -> Tuple[float, float, float]:
        """Return demand, supply and combined confidence."""

        demand_forecast = self.demand_forecaster.forecast(
            snapshot.config.name, snapshot.energy_status, snapshot.disaster_event.severity
        )
        supply_forecast = self.supply_forecaster.forecast(
            snapshot.config.name,
            snapshot.energy_status,
            snapshot.disaster_event.infrastructure_impact,
        )
        combined_confidence = min(demand_forecast.confidence, supply_forecast.confidence)
        forecast_supply = (
            supply_forecast.generation_mw if supply_forecast.generation_mw > 0 else snapshot.energy_status.generation_mw
        )
        storage_contribution = min(
            snapshot.energy_status.stored_mwh,
            snapshot.config.storage_capacity_mwh,
        ) * snapshot.config.storage_efficiency / 4
        forecast_supply += storage_contribution
        forecast_demand = (
            demand_forecast.demand_mw if demand_forecast.demand_mw > 0 else snapshot.energy_status.demand_mw
        )
        return forecast_demand, forecast_supply, combined_confidence

    def _connection_map(self) -> Dict[str, Iterable[GridConnection]]:
        mapping: Dict[str, List[GridConnection]] = {}
        for region in self.region_configs.values():
            for connection in region.grid_connections:
                mapping.setdefault(connection.target_region, []).append(
                    GridConnection(
                        target_region=region.name,
                        capacity_mw=connection.capacity_mw,
                        loss_factor=connection.loss_factor,
                    )
                )
        return mapping

    def run_cycle(self, snapshots: List[RegionalSnapshot]) -> EnergyDispatchPlan:
        """Execute a forecasting + optimisation cycle for the given snapshots."""

        region_demand: Dict[str, float] = {}
        region_supply: Dict[str, float] = {}
        confidence_tracker: Dict[str, float] = {}

        for snapshot in snapshots:
            demand, supply, confidence = self._forecast_region(snapshot)
            region_demand[snapshot.config.name] = demand
            region_supply[snapshot.config.name] = supply
            confidence_tracker[snapshot.config.name] = confidence

        plan = self.optimizer.optimise(
            region_supply=region_supply,
            region_demand=region_demand,
            connections=self._connection_map(),
        )

        # Filter out dispatches below the AI confidence threshold.
        filtered_dispatches = []
        for dispatch in plan.dispatches:
            confidence = min(
                confidence_tracker.get(dispatch.source, 1.0),
                confidence_tracker.get(dispatch.target, 1.0),
            )
            if confidence < self.optimizer.params.ai_confidence_threshold:
                continue
            filtered_dispatches.append(dispatch)

        return EnergyDispatchPlan(dispatches=filtered_dispatches)

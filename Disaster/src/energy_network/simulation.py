"""Scenario simulation harness for the energy sharing network."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from .config import OptimizationParameters, RegionConfig
from .data_ingestion import DisasterEvent, EnergyStatus, RegionalDataIngestor
from .optimization import EnergyAllocationOptimizer
from .orchestrator import EnergyOrchestrator, RegionalSnapshot


@dataclass
class SimulationResult:
    """Collection of dispatch plans for an executed scenario."""

    scenario: str
    dispatch_logs: List[Dict[str, float]]


class SimulationRunner:
    """High level API for running end-to-end simulations."""

    def __init__(
        self,
        data_root: Path,
        region_configs: Iterable[RegionConfig],
        optimization_params: OptimizationParameters | None = None,
    ) -> None:
        self.ingestor = RegionalDataIngestor(data_root=data_root)
        self.region_configs: Dict[str, RegionConfig] = {config.name: config for config in region_configs}
        self.optimization_params = optimization_params or OptimizationParameters()

    def _initial_snapshots(self, scenario: str) -> List[RegionalSnapshot]:
        baseline = self.ingestor.load_energy_baseline(scenario)
        events = list(self.ingestor.load_disaster_events(scenario))
        events_by_region: Dict[str, DisasterEvent] = {
            event.region: event for event in events
        }

        snapshots: List[RegionalSnapshot] = []
        for region_name, config in self.region_configs.items():
            snapshots.append(
                RegionalSnapshot(
                    config=config,
                    energy_status=baseline.get(
                        region_name,
                        EnergyStatus(
                            demand_mw=config.base_demand_mw,
                            generation_mw=config.base_generation_mw,
                            stored_mwh=config.storage_capacity_mwh / 2,
                        ),
                    ),
                    disaster_event=events_by_region.get(
                        region_name,
                        DisasterEvent(
                            region=region_name,
                            event_type="none",
                            severity=0.0,
                            infrastructure_impact=0.0,
                            description="Baseline operation",
                        ),
                    ),
                )
            )
        return snapshots

    def run(self, scenario: str) -> SimulationResult:
        optimizer = EnergyAllocationOptimizer(self.optimization_params)
        orchestrator = EnergyOrchestrator(self.region_configs, optimizer)

        snapshots = self._initial_snapshots(scenario)
        plan = orchestrator.run_cycle(snapshots)

        dispatch_logs = [
            {
                "source": dispatch.source,
                "target": dispatch.target,
                "transfer_mw": dispatch.transfer_mw,
                "loss_mw": dispatch.loss_mw,
            }
            for dispatch in plan.dispatches
        ]

        return SimulationResult(scenario=scenario, dispatch_logs=dispatch_logs)

"""Data ingestion utilities for disaster-aware energy orchestration."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


@dataclass
class DisasterEvent:
    """Represents a disaster impacting a region at a specific time."""

    region: str
    event_type: str
    severity: float
    infrastructure_impact: float
    description: str


@dataclass
class EnergyStatus:
    """Snapshot of demand, generation and storage conditions."""

    demand_mw: float
    generation_mw: float
    stored_mwh: float

    @property
    def net_balance(self) -> float:
        """Positive when there is surplus generation."""

        return self.generation_mw - self.demand_mw


class RegionalDataIngestor:
    """Loads regional disaster and energy context data."""

    def __init__(self, data_root: Path) -> None:
        self.data_root = data_root

    def load_disaster_events(self, scenario_name: str) -> Iterable[DisasterEvent]:
        """Load a stream of disaster events from a JSON scenario file."""

        scenario_path = self.data_root / f"{scenario_name}.json"
        with scenario_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        for entry in payload.get("events", []):
            yield DisasterEvent(
                region=entry["region"],
                event_type=entry["event_type"],
                severity=float(entry.get("severity", 0.0)),
                infrastructure_impact=float(entry.get("infrastructure_impact", 0.0)),
                description=entry.get("description", ""),
            )

    def load_energy_baseline(self, scenario_name: str) -> Dict[str, EnergyStatus]:
        """Load baseline energy states per region for a scenario."""

        scenario_path = self.data_root / f"{scenario_name}.json"
        with scenario_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        baseline: Dict[str, EnergyStatus] = {}
        for region, stats in payload.get("baseline", {}).items():
            baseline[region] = EnergyStatus(
                demand_mw=float(stats["demand_mw"]),
                generation_mw=float(stats["generation_mw"]),
                stored_mwh=float(stats["stored_mwh"]),
            )
        return baseline

    def region_list(self, scenario_name: str) -> List[str]:
        """Return a list of regions represented in a scenario file."""

        scenario_path = self.data_root / f"{scenario_name}.json"
        with scenario_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return list(payload.get("baseline", {}).keys())

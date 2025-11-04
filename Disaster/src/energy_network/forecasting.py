"""Simple forecasting utilities for energy demand and supply."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from .data_ingestion import EnergyStatus


@dataclass
class ForecastResult:
    demand_mw: float
    generation_mw: float
    confidence: float


def _moving_average(values: Iterable[float]) -> float:
    data = list(values)
    if not data:
        return 0.0
    return sum(data) / len(data)


@dataclass
class DemandForecaster:
    """Forecasts demand based on recent history and disaster severity."""

    history_size: int = 4
    disaster_penalty: float = 0.15
    history: Dict[str, List[float]] = field(default_factory=dict)

    def update_history(self, region: str, demand: float) -> None:
        self.history.setdefault(region, []).append(demand)
        if len(self.history[region]) > self.history_size:
            self.history[region] = self.history[region][-self.history_size :]

    def forecast(self, region: str, current: EnergyStatus, severity: float) -> ForecastResult:
        self.update_history(region, current.demand_mw)
        trend = _moving_average(self.history.get(region, []))
        adjustment = 1 + self.disaster_penalty * severity
        forecast_value = trend * adjustment
        confidence = max(0.3, 1.0 - self.disaster_penalty * severity)
        return ForecastResult(demand_mw=forecast_value, generation_mw=0.0, confidence=confidence)


@dataclass
class SupplyForecaster:
    """Forecasts generation capacity including infrastructure impacts."""

    history_size: int = 4
    impact_penalty: float = 0.2
    history: Dict[str, List[float]] = field(default_factory=dict)

    def update_history(self, region: str, generation: float) -> None:
        self.history.setdefault(region, []).append(generation)
        if len(self.history[region]) > self.history_size:
            self.history[region] = self.history[region][-self.history_size :]

    def forecast(self, region: str, current: EnergyStatus, infrastructure_impact: float) -> ForecastResult:
        self.update_history(region, current.generation_mw)
        trend = _moving_average(self.history.get(region, []))
        adjustment = max(0.0, 1 - self.impact_penalty * infrastructure_impact)
        forecast_value = trend * adjustment
        confidence = max(0.2, adjustment)
        return ForecastResult(demand_mw=0.0, generation_mw=forecast_value, confidence=confidence)

"""Configuration dataclasses for the AI-Orchestrated energy network."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GridConnection:
    """Represents a cross-border interconnection between two regions."""

    target_region: str
    capacity_mw: float
    loss_factor: float = 0.05


@dataclass
class RegionConfig:
    """Static configuration for a region participating in the network."""

    name: str
    base_demand_mw: float
    base_generation_mw: float
    storage_capacity_mwh: float
    storage_efficiency: float = 0.9
    grid_connections: List[GridConnection] = field(default_factory=list)


@dataclass
class OptimizationParameters:
    """Parameters controlling the orchestration heuristics."""

    max_transfer_fraction: float = 0.6
    reserve_margin_fraction: float = 0.05
    ramp_limit_mw: float = 200.0
    ai_confidence_threshold: float = 0.55

    def to_dict(self) -> Dict[str, float]:
        """Export parameters to a JSON-serialisable dictionary."""

        return {
            "max_transfer_fraction": self.max_transfer_fraction,
            "reserve_margin_fraction": self.reserve_margin_fraction,
            "ramp_limit_mw": self.ramp_limit_mw,
            "ai_confidence_threshold": self.ai_confidence_threshold,
        }

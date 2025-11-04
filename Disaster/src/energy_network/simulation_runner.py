"""Command-line entry point for running sample simulations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import GridConnection, OptimizationParameters, RegionConfig
from .simulation import SimulationRunner


def _default_region_configs() -> list[RegionConfig]:
    return [
        RegionConfig(
            name="Japan",
            base_demand_mw=50000,
            base_generation_mw=52000,
            storage_capacity_mwh=15000,
            grid_connections=[
                GridConnection(target_region="Korea", capacity_mw=2000, loss_factor=0.07),
                GridConnection(target_region="EU", capacity_mw=1200, loss_factor=0.12),
            ],
        ),
        RegionConfig(
            name="Korea",
            base_demand_mw=35000,
            base_generation_mw=37000,
            storage_capacity_mwh=10000,
            grid_connections=[
                GridConnection(target_region="Japan", capacity_mw=2000, loss_factor=0.07),
                GridConnection(target_region="EU", capacity_mw=1500, loss_factor=0.1),
            ],
        ),
        RegionConfig(
            name="EU",
            base_demand_mw=60000,
            base_generation_mw=64000,
            storage_capacity_mwh=25000,
            grid_connections=[
                GridConnection(target_region="Japan", capacity_mw=1200, loss_factor=0.12),
                GridConnection(target_region="Korea", capacity_mw=1500, loss_factor=0.1),
            ],
        ),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scenario",
        default="sample_transnational_event",
        help="Scenario file (without .json) to execute from the data/ directory.",
    )
    parser.add_argument(
        "--data-root",
        default=Path(__file__).resolve().parents[2] / "data",
        type=Path,
        help="Path to the directory containing scenario JSON files.",
    )
    args = parser.parse_args()

    runner = SimulationRunner(
        data_root=args.data_root,
        region_configs=_default_region_configs(),
        optimization_params=OptimizationParameters(),
    )
    result = runner.run(args.scenario)
    print(json.dumps({"scenario": result.scenario, "dispatches": result.dispatch_logs}, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()

from pathlib import Path

from energy_network.config import GridConnection, OptimizationParameters, RegionConfig
from energy_network.data_ingestion import DisasterEvent, EnergyStatus
from energy_network.optimization import EnergyAllocationOptimizer
from energy_network.orchestrator import EnergyOrchestrator, RegionalSnapshot
from energy_network.simulation import SimulationRunner


def _region_configs():
    return {
        "Japan": RegionConfig(
            name="Japan",
            base_demand_mw=50000,
            base_generation_mw=52000,
            storage_capacity_mwh=15000,
            grid_connections=[
                GridConnection(target_region="Korea", capacity_mw=2000, loss_factor=0.05),
                GridConnection(target_region="EU", capacity_mw=1500, loss_factor=0.1),
            ],
        ),
        "Korea": RegionConfig(
            name="Korea",
            base_demand_mw=34000,
            base_generation_mw=36000,
            storage_capacity_mwh=9000,
            grid_connections=[
                GridConnection(target_region="Japan", capacity_mw=2000, loss_factor=0.05),
                GridConnection(target_region="EU", capacity_mw=1400, loss_factor=0.1),
            ],
        ),
        "EU": RegionConfig(
            name="EU",
            base_demand_mw=62000,
            base_generation_mw=65000,
            storage_capacity_mwh=22000,
            grid_connections=[
                GridConnection(target_region="Japan", capacity_mw=1500, loss_factor=0.1),
                GridConnection(target_region="Korea", capacity_mw=1400, loss_factor=0.1),
            ],
        ),
    }


def test_energy_orchestrator_generates_dispatch_plan(tmp_path: Path):
    region_configs = _region_configs()
    optimizer = EnergyAllocationOptimizer(OptimizationParameters())
    orchestrator = EnergyOrchestrator(region_configs, optimizer)

    snapshots = [
        RegionalSnapshot(
            config=region_configs["Japan"],
            energy_status=EnergyStatus(demand_mw=52000, generation_mw=48000, stored_mwh=8000),
            disaster_event=DisasterEvent(
                region="Japan",
                event_type="earthquake",
                severity=0.6,
                infrastructure_impact=0.3,
                description="Test earthquake",
            ),
        ),
        RegionalSnapshot(
            config=region_configs["Korea"],
            energy_status=EnergyStatus(demand_mw=35000, generation_mw=40000, stored_mwh=9000),
            disaster_event=DisasterEvent(
                region="Korea",
                event_type="typhoon",
                severity=0.4,
                infrastructure_impact=0.2,
                description="Test typhoon",
            ),
        ),
        RegionalSnapshot(
            config=region_configs["EU"],
            energy_status=EnergyStatus(demand_mw=60000, generation_mw=66000, stored_mwh=21000),
            disaster_event=DisasterEvent(
                region="EU",
                event_type="heatwave",
                severity=0.2,
                infrastructure_impact=0.1,
                description="Test heatwave",
            ),
        ),
    ]

    plan = orchestrator.run_cycle(snapshots)
    assert plan.dispatches, "Expected non-empty dispatch plan"
    assert all(dispatch.transfer_mw > 0 for dispatch in plan.dispatches)


def test_simulation_runner_returns_serialisable_result(tmp_path: Path):
    data_root = Path(__file__).resolve().parents[1] / "data"
    runner = SimulationRunner(
        data_root=data_root,
        region_configs=_region_configs().values(),
        optimization_params=OptimizationParameters(),
    )
    result = runner.run("sample_transnational_event")
    assert result.dispatch_logs, "Simulation should produce dispatch records"
    assert {"source", "target", "transfer_mw", "loss_mw"} <= result.dispatch_logs[0].keys()

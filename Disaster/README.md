# AI-Orchestrated Disaster-Resilient Energy Sharing Network

This repository implements a prototype AI coordination layer for a cross-border energy
sharing network spanning Japan, Korea and the European Union. The goal is to orchestrate
fast disaster-aware balancing of electricity demand and supply using lightweight
forecasting and optimisation components.

## Features

- **Scenario-driven simulation** – ingest JSON disaster scenarios describing baseline
  energy states and disruptive events.
- **Demand & supply forecasting** – moving-average based forecasting layers that adapt
  to disaster severity and infrastructure impact signals.
- **Cross-border optimisation** – heuristic allocation algorithm that respects transfer
  capacities, losses and policy constraints.
- **End-to-end orchestration** – modular orchestrator that stitches forecasts with the
  optimisation engine to produce dispatch plans.

## Project structure

```
├── data/
│   └── sample_transnational_event.json   # Example disaster scenario
├── src/
│   └── energy_network/
│       ├── __init__.py
│       ├── config.py                     # Region & optimisation configuration models
│       ├── data_ingestion.py             # Scenario ingestion utilities
│       ├── forecasting.py                # Demand & supply forecasting logic
│       ├── optimization.py               # Heuristic dispatcher
│       ├── orchestrator.py               # Core orchestration workflow
│       └── simulation.py                 # Scenario runner façade
└── tests/
    └── test_orchestrator.py              # Regression coverage for dispatch logic
```

## Getting started

1. **Install dependencies**

   ```bash
   pip install -e .[dev]
   ```

2. **Execute the sample simulation**

   ```bash
   python -m energy_network.simulation_runner
   ```

   The command prints the computed dispatch plan for the sample scenario.

3. **Run the test-suite**

   ```bash
   pytest
   ```

## Extending the model

- Replace the simple moving average forecasters with ML-based predictors such as
  Prophet, XGBoost or RNNs using real telemetry.
- Swap the heuristic dispatcher with a linear optimisation solver (e.g. PuLP, OR-Tools).
- Add more granular time-stepped simulation and demand response controls.

## License

This project is released under the MIT license.

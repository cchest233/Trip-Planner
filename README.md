# Trip-Planner

Minimal LangGraph + LangChain backend that turns a structured CLI request into a demo trip plan JSON. The focus is on wiring, interfaces, and data flow while leaving space for future real providers.

## Features

- Five-node LangGraph pipeline (router, fetcher, routing, scheduler, narrator).
- Provider interfaces for POI, routing, and weather data with demo implementations.
- Pydantic models for all core schemas and LangChain-based narration.
- Scheduler that clusters POIs with KMeans and builds day plans with pacing heuristics.
- CLI that emits a `TripPlan` JSON to stdout and saves a copy under `output/`.

## Getting Started

1. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

_Minimal requirements (for reference)_:

```text
langgraph
langchain
pydantic
scikit-learn
numpy
```

2. Copy `.env.example` to `.env` and adjust values as needed. Leaving keys empty keeps the demo providers active.

3. Generate a sample itinerary:

```bash
python -m src.app \
  --city "Kyoto" \
  --start 2025-04-02 \
  --end 2025-04-04 \
  --party 2 \
  --mode walk \
  --pace medium \
  --themes food museum
```

The command prints the `TripPlan` JSON and writes `output/trip_<date>.json`.

4. Run unit tests:

```bash
pytest
```

## Repository Structure

```
src/
  app.py
  config.py
  graph.py
  llm/
    client.py
  logic/
    router_node.py
    fetcher_node.py
    routing_node.py
    scheduler_node.py
    narrator_node.py
  models.py
  services/
    pois.py
    routing.py
    weather.py
  storage/
    cache.py
  utils/
    geo.py
    timebox.py
tests/
  test_scheduler_utils.py
  sample_inputs/
    paris_short.json
```

The current implementation is intentionally lightweight: external calls are stubbed behind interfaces and can be replaced once provider decisions are made.

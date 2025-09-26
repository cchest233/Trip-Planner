"""CLI entrypoint for the trip planner graph."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any, Dict

from pydantic.json import pydantic_encoder

from src.graph import build_graph
from src.models import DateRange, TripConstraints


OUTPUT_DIR = Path("output")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a demo trip plan.")
    parser.add_argument("--city", required=True)
    parser.add_argument("--start", required=True, help="Trip start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="Trip end date (YYYY-MM-DD)")
    parser.add_argument("--party", type=int, default=2, help="Party size")
    parser.add_argument("--mode", choices=["walk", "transit", "drive"], default="walk")
    parser.add_argument(
        "--pace", choices=["relaxed", "medium", "tight"], default="medium"
    )
    parser.add_argument(
        "--themes",
        nargs="*",
        default=[],
        help="Optional list of themes (e.g. food museum)",
    )
    return parser.parse_args()


def build_initial_state(args: argparse.Namespace) -> Dict[str, Any]:
    constraints = TripConstraints(
        city=args.city,
        dates=DateRange(start=date.fromisoformat(args.start), end=date.fromisoformat(args.end)),
        party_size=args.party,
        mode=args.mode,
        pace=args.pace,
        themes=args.themes,
    )
    return {"constraints": constraints}


def run() -> None:
    args = parse_args()
    state = build_initial_state(args)
    graph = build_graph().compile()
    result = graph.invoke(state)
    trip_plan = result["trip_plan"]

    payload = json.dumps(trip_plan.dict(), indent=2, default=pydantic_encoder)
    print(payload)

    OUTPUT_DIR.mkdir(exist_ok=True)
    filename = OUTPUT_DIR / f"trip_{date.today().isoformat()}.json"
    filename.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    run()

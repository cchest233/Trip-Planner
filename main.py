"""
CLI entrypoint for the road trip planner.

Usage:
    python main.py "I want to drive from SF to LA in 3 days, I like food"
    python main.py --query "Plan a Seattle to Portland road trip"
    python main.py --interactive
"""

import sys
import json
import argparse
from typing import Any

from roadtrip_planner.state import RoadTripState, get_state_summary
from roadtrip_planner.graph import build_road_trip_graph
from roadtrip_planner.config import config


def print_separator(char: str = "=", length: int = 80) -> None:
    """Print a separator line."""
    print(char * length)


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f" {title}")
    print(f"{'=' * 80}\n")


def print_debug_trace(state: RoadTripState) -> None:
    """Print the debug trace in a readable format."""
    print_section("DEBUG TRACE")
    
    if not state.debug_trace:
        print("(No debug events recorded)")
        return
    
    for event in state.debug_trace:
        timestamp = event.get("timestamp", "N/A")
        node = event.get("node", "unknown")
        event_type = event.get("event_type", "info")
        message = event.get("message", "")
        
        # Color code based on event type (basic ANSI colors)
        color_codes = {
            "start": "\033[94m",      # Blue
            "complete": "\033[92m",   # Green
            "error": "\033[91m",      # Red
            "info": "\033[93m",       # Yellow
        }
        reset_code = "\033[0m"
        
        color = color_codes.get(event_type, "")
        
        print(f"{color}[{timestamp}] {node} ({event_type}){reset_code}")
        print(f"  {message}")
        
        if "snapshot" in event:
            snapshot_str = json.dumps(event["snapshot"], indent=2)
            print(f"  Snapshot: {snapshot_str}")
        print()


def print_itinerary(state: RoadTripState) -> None:
    """Print the final itinerary."""
    print_section("YOUR ROAD TRIP ITINERARY")
    
    if state.itinerary_text:
        print(state.itinerary_text)
    else:
        print("(No itinerary generated)")
    
    # Print summary statistics
    if state.itinerary:
        print("\n" + "-" * 80)
        print(f"Total Days: {len(state.itinerary.days)}")
        if state.itinerary.total_drive_hours:
            print(f"Total Driving Time: {state.itinerary.total_drive_hours:.1f} hours")
        total_pois = sum(len(day.stops) for day in state.itinerary.days)
        print(f"Total Stops/POIs: {total_pois}")
        print("-" * 80)


def print_state_summary(state: RoadTripState) -> None:
    """Print a summary of the state."""
    print_section("STATE SUMMARY")
    
    summary = get_state_summary(state)
    for key, value in summary.items():
        print(f"  {key}: {value}")


def run_planner(query: str, verbose: bool = False, debug: bool = False) -> RoadTripState:
    """
    Run the road trip planner with the given query.

    Args:
        query: Natural language query describing the road trip
        verbose: Whether to print verbose output
        debug: Whether to print debug trace

    Returns:
        Final RoadTripState after workflow execution
    """
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease set the required environment variables in a .env file:")
        print("  OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    # Create initial state
    initial_state = RoadTripState(user_query=query)
    
    if verbose:
        print_section("STARTING ROAD TRIP PLANNER")
        print(f"Query: {query}\n")
    
    try:
        # Build and run the graph
        graph = build_road_trip_graph()
        
        if verbose:
            print("Executing workflow...")
            print()
        
        # Invoke the graph
        final_state = graph.invoke(initial_state)
        
        if verbose:
            print("\nWorkflow completed successfully!")
        
        return final_state
    
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        if debug:
            import traceback
            print("\nFull traceback:")
            traceback.print_exc()
        sys.exit(1)


def interactive_mode() -> None:
    """Run the planner in interactive mode."""
    print_section("INTERACTIVE ROAD TRIP PLANNER")
    print("Enter your road trip requests. Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            query = input("Your request: ").strip()
            
            if query.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye! Happy travels! 🚗")
                break
            
            if not query:
                continue
            
            # Run planner
            state = run_planner(query, verbose=True, debug=False)
            
            # Print results
            print_itinerary(state)
            
            # Ask if user wants debug info
            show_debug = input("\nShow debug trace? (y/n): ").strip().lower()
            if show_debug == "y":
                print_debug_trace(state)
            
            print("\n" + "=" * 80 + "\n")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! Happy travels! 🚗")
            break
        except Exception as e:
            print(f"\nError: {e}")
            continue


def main() -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Plan a road trip using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "I want to drive from SF to LA in 3 days, I like coastal views"
  python main.py --query "Plan a 4-day road trip from Seattle to Portland"
  python main.py --interactive
  python main.py "SF to LA road trip" --debug
        """
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural language road trip request"
    )
    parser.add_argument(
        "--query", "-q",
        dest="query_arg",
        help="Alternative way to specify query"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print verbose output"
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Print debug trace"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save itinerary to file"
    )
    
    args = parser.parse_args()
    
    # Handle interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Get query from args
    query = args.query or args.query_arg
    
    if not query:
        parser.print_help()
        print("\n❌ Error: Please provide a query or use --interactive mode")
        sys.exit(1)
    
    # Run planner
    state = run_planner(query, verbose=args.verbose or args.debug, debug=args.debug)
    
    # Print results
    if not args.verbose:
        print_section("YOUR ROAD TRIP ITINERARY")
    
    print_itinerary(state)
    
    # Print debug trace if requested
    if args.debug:
        print_debug_trace(state)
        print_state_summary(state)
    
    # Save to file if requested
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            if state.itinerary_text:
                f.write(state.itinerary_text)
                f.write("\n\n")
            
            # Also save structured data as JSON
            if state.itinerary:
                f.write("\n---\nStructured Data (JSON):\n")
                f.write(state.itinerary.model_dump_json(indent=2))
        
        print(f"\n✅ Itinerary saved to: {args.output}")


if __name__ == "__main__":
    main()

"""
Test run script to verify the road trip planner is working correctly.

This script performs a simple end-to-end test with a basic query.
"""

import sys
import traceback
from roadtrip_planner.state import RoadTripState
from roadtrip_planner.graph import build_road_trip_graph
from roadtrip_planner.config import config


def print_section(title: str, char: str = "=") -> None:
    """Print a formatted section header."""
    print(f"\n{char * 80}")
    print(f" {title}")
    print(f"{char * 80}\n")


def test_configuration() -> bool:
    """Test if configuration is properly set up."""
    print_section("Step 1: Testing Configuration", "-")
    
    try:
        # Check if API key is set
        if not config.OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY is not set!")
            print("   Please set it in your .env file")
            return False
        
        print(f"✅ API Key: {'*' * 20}{config.OPENAI_API_KEY[-4:]}")
        
        # Check base URL
        if config.OPENAI_BASE_URL:
            print(f"✅ Base URL: {config.OPENAI_BASE_URL}")
            print("   (Using custom endpoint - Silicon Flow)")
        else:
            print("✅ Base URL: Default OpenAI endpoint")
        
        # Check model configuration
        print(f"✅ Parser Model: {config.PARSER_MODEL}")
        print(f"✅ Planner Model: {config.PLANNER_MODEL}")
        print(f"✅ Renderer Model: {config.RENDERER_MODEL}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_simple_query() -> bool:
    """Test a simple query through the entire workflow."""
    print_section("Step 2: Testing Simple Query", "-")
    
    # Simple test query
    test_query = "I want to drive from San Francisco to Los Angeles in 2 days, I like coastal views"
    
    print(f"Test Query: \"{test_query}\"\n")
    
    try:
        # Create initial state
        print("Creating initial state...")
        initial_state = RoadTripState(user_query=test_query)
        print("✅ Initial state created\n")
        
        # Build graph
        print("Building LangGraph workflow...")
        graph = build_road_trip_graph()
        print("✅ Graph built successfully\n")
        
        # Run the workflow
        print("Running workflow (this may take 30-60 seconds)...")
        print("Please wait...\n")
        
        result = graph.invoke(initial_state)
        
        print("✅ Workflow completed!\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error during workflow execution:")
        print(f"   {type(e).__name__}: {e}\n")
        traceback.print_exc()
        return None


def print_results(result) -> None:
    """Print the results of the test run."""
    print_section("Step 3: Results", "-")
    
    # LangGraph returns a dict, so we need to access fields as dict keys
    # Check parsed request
    request = result.get("request")
    if request:
        print("✅ Request Parsing:")
        print(f"   Origin: {request.origin}")
        print(f"   Destination: {request.destination}")
        print(f"   Days: {request.num_days}")
        print(f"   Max Drive Hours/Day: {request.max_drive_hours_per_day}")
        print(f"   Preferences: Nature={request.preferences.nature}, "
              f"City={request.preferences.city}, "
              f"Food={request.preferences.food}")
    else:
        print("❌ Request parsing failed")
    
    # Check media search
    media_items = result.get("media_items", [])
    print(f"\n✅ Media Search: Found {len(media_items)} items")
    if media_items:
        for i, item in enumerate(media_items[:3], 1):
            print(f"   {i}. {item.title} (score: {item.score})")
        if len(media_items) > 3:
            print(f"   ... and {len(media_items) - 3} more")
    
    # Check route skeleton
    route_skeleton = result.get("route_skeleton")
    if route_skeleton:
        print(f"\n✅ Route Skeleton: {len(route_skeleton.days)} days planned")
        for day in route_skeleton.days:
            print(f"   Day {day.day_index}: {day.start_location} → {day.end_location}")
            print(f"      Candidate stops: {', '.join(day.candidate_stops[:3])}")
    else:
        print("\n❌ Route skeleton generation failed")
    
    # Check daily plans
    daily_plan = result.get("daily_plan", [])
    if daily_plan:
        total_pois = sum(len(plan.stops) for plan in daily_plan)
        print(f"\n✅ Daily Plans: {len(daily_plan)} days, {total_pois} POIs selected")
        for plan in daily_plan:
            print(f"   Day {plan.day_index}: {len(plan.stops)} stops")
            for poi in plan.stops[:2]:
                print(f"      - {poi.name} ({poi.category})")
    else:
        print("\n❌ Daily plan generation failed")
    
    # Check itinerary
    itinerary_text = result.get("itinerary_text")
    if itinerary_text:
        print(f"\n✅ Itinerary Generated: {len(itinerary_text)} characters")
    else:
        print("\n❌ Itinerary rendering failed")
    
    # Debug trace
    debug_trace = result.get("debug_trace", [])
    print(f"\n✅ Debug Trace: {len(debug_trace)} events recorded")
    
    # Print the actual itinerary
    print_section("Final Itinerary")
    if itinerary_text:
        print(itinerary_text)
    else:
        print("(No itinerary generated)")


def print_debug_summary(result) -> None:
    """Print a summary of debug events."""
    print_section("Debug Summary", "-")
    
    debug_trace = result.get("debug_trace", [])
    for event in debug_trace:
        event_type = event.get('event_type', 'info')
        node = event.get('node', 'unknown')
        message = event.get('message', '')
        
        # Simple emoji indicators
        emoji = {
            'start': '🔵',
            'complete': '✅',
            'error': '❌',
            'info': 'ℹ️'
        }.get(event_type, '•')
        
        print(f"{emoji} [{node}] {message}")


def main():
    """Main test function."""
    print_section("ROAD TRIP PLANNER - TEST RUN", "=")
    print("This script will test the entire workflow with a simple query.\n")
    
    # Step 1: Test configuration
    if not test_configuration():
        print("\n❌ Configuration test failed. Please fix the issues above.")
        sys.exit(1)
    
    # Step 2: Run simple query
    result = test_simple_query()
    
    if result is None:
        print("\n❌ Test run failed. Check the error messages above.")
        sys.exit(1)
    
    # Step 3: Print results
    print_results(result)
    
    # Step 4: Debug summary
    print_debug_summary(result)
    
    # Final summary
    print_section("Test Summary", "=")
    
    success_checks = [
        ("Configuration", True),
        ("Request Parsing", result.get("request") is not None),
        ("Media Search", len(result.get("media_items", [])) > 0),
        ("Route Skeleton", result.get("route_skeleton") is not None),
        ("Daily Plans", len(result.get("daily_plan", [])) > 0),
        ("Itinerary", result.get("itinerary_text") is not None),
    ]
    
    passed = sum(1 for _, check in success_checks if check)
    total = len(success_checks)
    
    print(f"Tests Passed: {passed}/{total}\n")
    
    for name, check in success_checks:
        status = "✅ PASS" if check else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print()
    
    if passed == total:
        print("🎉 All tests passed! Your road trip planner is working correctly!")
        print("\nYou can now use it with:")
        print('  python main.py "your road trip query here"')
        print("  python main.py --interactive")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)

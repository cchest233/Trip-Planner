"""
Test script with detailed logging enabled.

This demonstrates the new logging feature that shows progress through each LangGraph node.
"""

from roadtrip_planner.state import RoadTripState
from roadtrip_planner.graph import build_road_trip_graph
from roadtrip_planner.config import config


def main():
    """Run a test with detailed logging."""
    print("\n" + "=" * 80)
    print(" ROAD TRIP PLANNER - TEST WITH DETAILED LOGGING")
    print("=" * 80)
    print()
    print("This test will show you detailed progress through each step:")
    print("  🔵 = Node starting")
    print("  ✅ = Node completed")
    print("  • = Step within a node")
    print("  📤 = Output from a step")
    print()
    print("=" * 80)
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("Please set OPENAI_API_KEY in your .env file")
        return
    
    # Create test query
    test_query = "I want to drive from San Francisco to Los Angeles in 2 days, I love coastal views and seafood"
    
    print(f"\n📝 Test Query: \"{test_query}\"")
    print()
    
    # Create initial state
    initial_state = RoadTripState(user_query=test_query)
    
    # Build and run graph
    graph = build_road_trip_graph()
    
    print("🚀 Starting workflow...\n")
    
    try:
        result = graph.invoke(initial_state)
        
        print("\n" + "=" * 80)
        print(" ✅ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        
        # Print final itinerary
        if result.get("itinerary_text"):
            print("📋 FINAL ITINERARY:")
            print("=" * 80)
            print(result["itinerary_text"])
            print("=" * 80)
        else:
            print("⚠️  No itinerary text generated")
        
        print()
        print("✨ Test completed! You can now see the detailed progress of each step.")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

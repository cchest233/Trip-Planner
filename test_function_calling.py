"""
Test script for Function Calling / Tool Use feature.

This demonstrates how the LLM can call tools to gather real-time information
before generating responses.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from roadtrip_planner.llm_clients import call_llm_with_tools
from roadtrip_planner.tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS


def test_simple_tool_call():
    """Test a simple question that should trigger tool use."""
    
    print("=" * 80)
    print("TEST 1: Simple Distance Calculation")
    print("=" * 80)
    print()
    
    query = "How far is it from San Francisco to Los Angeles and how long does it take to drive?"
    
    print(f"Query: {query}")
    print()
    print("Calling LLM with tools...")
    print()
    
    result = call_llm_with_tools(
        prompt=query,
        tools=TOOL_DEFINITIONS,
        tool_functions=TOOL_FUNCTIONS
    )
    
    print("-" * 80)
    print("RESULT:")
    print("-" * 80)
    print(result['content'])
    print()
    
    if result['tool_calls']:
        print("-" * 80)
        print(f"TOOLS CALLED: {len(result['tool_calls'])}")
        print("-" * 80)
        for i, tool_call in enumerate(result['tool_calls'], 1):
            print(f"\n{i}. {tool_call['name']}")
            print(f"   Arguments: {tool_call['arguments']}")
            print(f"   Result: {tool_call['result']}")
    
    print()
    print(f"Total iterations: {result['iterations']}")
    print()


def test_multiple_locations():
    """Test a query that requires multiple tool calls."""
    
    print("=" * 80)
    print("TEST 2: Multiple Location Queries")
    print("=" * 80)
    print()
    
    query = """
I need to know:
1. Distance from San Francisco to Monterey
2. Distance from Monterey to Los Angeles
3. What restaurants are near Monterey
"""
    
    print(f"Query: {query}")
    print()
    print("Calling LLM with tools...")
    print()
    
    result = call_llm_with_tools(
        prompt=query,
        tools=TOOL_DEFINITIONS,
        tool_functions=TOOL_FUNCTIONS,
        max_iterations=10  # Allow more iterations
    )
    
    print("-" * 80)
    print("RESULT:")
    print("-" * 80)
    print(result['content'])
    print()
    
    if result['tool_calls']:
        print("-" * 80)
        print(f"TOOLS CALLED: {len(result['tool_calls'])}")
        print("-" * 80)
        for i, tool_call in enumerate(result['tool_calls'], 1):
            print(f"\n{i}. {tool_call['name']}")
            print(f"   Arguments: {tool_call['arguments']}")
            print(f"   Result: {tool_call['result']}")
    
    print()
    print(f"Total iterations: {result['iterations']}")
    print()


def test_geocoding():
    """Test geocoding functionality."""
    
    print("=" * 80)
    print("TEST 3: Geocoding Test")
    print("=" * 80)
    print()
    
    query = "What are the coordinates of Golden Gate Bridge?"
    
    print(f"Query: {query}")
    print()
    print("Calling LLM with tools...")
    print()
    
    result = call_llm_with_tools(
        prompt=query,
        tools=TOOL_DEFINITIONS,
        tool_functions=TOOL_FUNCTIONS
    )
    
    print("-" * 80)
    print("RESULT:")
    print("-" * 80)
    print(result['content'])
    print()
    
    if result['tool_calls']:
        print("-" * 80)
        print(f"TOOLS CALLED: {len(result['tool_calls'])}")
        print("-" * 80)
        for i, tool_call in enumerate(result['tool_calls'], 1):
            print(f"\n{i}. {tool_call['name']}")
            print(f"   Arguments: {tool_call['arguments']}")
            print(f"   Result: {tool_call['result']}")
    
    print()


def main():
    """Run all tests."""
    
    print("\n")
    print("=" * 80)
    print("FUNCTION CALLING / TOOL USE TEST SUITE")
    print("=" * 80)
    print()
    print("This test demonstrates how the LLM can call tools to gather")
    print("information before generating responses.")
    print()
    print("NOTE: Currently using MOCK tools. Real API implementations needed.")
    print()
    
    try:
        # Run tests
        test_simple_tool_call()
        print("\n\n")
        
        test_multiple_locations()
        print("\n\n")
        
        test_geocoding()
        
        print("\n")
        print("=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80)
        print()
        print("✅ Function calling is working!")
        print()
        print("NEXT STEPS:")
        print("1. Implement real API calls in tools.py")
        print("2. Add tool calling to LangGraph nodes")
        print("3. Test with real Google Maps / Amap APIs")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

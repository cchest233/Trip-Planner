"""
Simplified test script - minimal test to verify basic LLM connectivity.

This is a quick test to ensure your Silicon Flow API key and model are working.
"""

from roadtrip_planner.config import config
from roadtrip_planner.llm_clients import call_parser_model
from roadtrip_planner.models import RoadTripRequest


def test_llm_connection():
    """Test basic LLM connection with a simple parsing task."""
    print("=" * 80)
    print(" SIMPLE LLM CONNECTION TEST")
    print("=" * 80)
    print()
    
    # Check configuration
    print("Configuration:")
    print(f"  API Key: {'*' * 20}{config.OPENAI_API_KEY[-4:] if config.OPENAI_API_KEY else 'NOT SET'}")
    print(f"  Base URL: {config.OPENAI_BASE_URL or 'Default OpenAI'}")
    print(f"  Parser Model: {config.PARSER_MODEL}")
    print()
    
    if not config.OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY is not set!")
        print("   Please set it in your .env file")
        return False
    
    # Test simple parsing
    print("Testing LLM with a simple query...")
    print()
    
    test_query = "I want to drive from Beijing to Shanghai in 3 days"
    print(f'Query: "{test_query}"')
    print()
    print("Calling LLM... (this may take 10-20 seconds)")
    
    try:
        result = call_parser_model(
            prompt=f'Parse this road trip request: "{test_query}"',
            output_model=RoadTripRequest
        )
        
        print()
        print("✅ SUCCESS! LLM responded correctly.")
        print()
        print("Parsed Result:")
        print(f"  Origin: {result.origin}")
        print(f"  Destination: {result.destination}")
        print(f"  Days: {result.num_days}")
        print(f"  Max Drive Hours: {result.max_drive_hours_per_day}")
        print()
        print("=" * 80)
        print("🎉 Your Silicon Flow API is working correctly!")
        print("=" * 80)
        print()
        print("Next step: Run the full test with:")
        print("  python test_run.py")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("❌ ERROR: LLM call failed!")
        print(f"   {type(e).__name__}: {e}")
        print()
        print("Common issues:")
        print("  1. Invalid API key")
        print("  2. Wrong base URL")
        print("  3. Model name incorrect")
        print("  4. Network connection issues")
        print()
        print("Please check your .env file:")
        print("  OPENAI_API_KEY=your_silicon_flow_key")
        print("  OPENAI_BASE_URL=https://api.siliconflow.cn/v1")
        print("  PARSER_MODEL=deepseek-ai/DeepSeek-V3.1-Terminus")
        print()
        
        return False


def main():
    """Run the simple test."""
    success = test_llm_connection()
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()

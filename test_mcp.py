# test_mcp.py
import asyncio
import sys

# Add parent directory to path for settings import
# sys.path.append(str(Path(__file__).parent.parent))
from main import mcp

async def test_mcp_tools():
    """Test MCP server tools directly."""
    print("🧪 Testing MCP Weather Server Tools")
    print("=" * 50)
    
    # Test location
    test_location = "Seattle"
    
    try:
        # Test 1: Current Weather
        print(f"\n1️⃣ Testing current weather for {test_location}...")
        weather_result = await mcp.call_tool("get_current_weather", {"location": test_location})
        print("✅ Current weather:", weather_result[:100] + "..." if len(weather_result) > 100 else weather_result)
        
    except Exception as e:
        print("❌ Current weather failed:", e)
    
    try:
        # Test 2: Weather Forecast
        print(f"\n2️⃣ Testing forecast for {test_location}...")
        forecast_result = await mcp.call_tool("get_weather_forecast", {"location": test_location})
        print("✅ Forecast:", forecast_result[:100] + "..." if len(forecast_result) > 100 else forecast_result)
        
    except Exception as e:
        print("❌ Forecast failed:", e)
    
    try:
        # Test 3: AI Insights (might take longer)
        print(f"\n3️⃣ Testing AI insights for {test_location}...")
        insights_result = await mcp.call_tool("get_weather_insights", {"location": test_location})
        print("✅ AI Insights:", insights_result[:100] + "..." if len(insights_result) > 100 else insights_result)
        
    except Exception as e:
        print("❌ AI insights failed:", e)
    
    print("\n🎉 MCP tool testing complete!")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
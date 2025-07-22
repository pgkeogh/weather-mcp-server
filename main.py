# main.py (root level)
import logging
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP

# Direct imports since services are at same level
from services.key_vault_service import KeyVaultService
from services.weather_service import WeatherService  
from services.ai_service import AIService
from config.settings import Settings

# Set up logging to stderr (MCP requirement)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("weather-server")

# Initialize services
key_vault_service = KeyVaultService()
weather_service = WeatherService(key_vault_service)
ai_service = AIService(key_vault_service)

@mcp.tool()
async def get_current_weather(location: str) -> str:
    """Get current weather for a location using OpenWeatherMap API."""
    try:
        logger.info("Getting current weather for: %s", location)
        weather_data = await weather_service.get_current_weather(location)
        
        return f"""Current weather in {location}:
Temperature: {weather_data.get('temp')}°F
Condition: {weather_data.get('description')}
Humidity: {weather_data.get('humidity')}%
Wind: {weather_data.get('wind_speed')} mph"""
        
    except Exception as e:
        logger.error("Weather request failed: %s", e)
        return f"Unable to get weather for {location}: {str(e)}"

@mcp.tool()
async def get_weather_forecast(location: str) -> str:
    """Get 5-day weather forecast for a location."""
    try:
        logger.info("Getting forecast for: %s", location)
        forecast_data = await weather_service.get_forecast(location)
        
        forecast_text = f"5-day forecast for {location}:\n"
        for day in forecast_data:
            forecast_text += f"\n{day['date']}: {day['temp_high']}°/{day['temp_low']}° - {day['description']}"
            
        return forecast_text
        
    except Exception as e:
        logger.error("Forecast request failed: %s", e)
        return f"Unable to get forecast for {location}: {str(e)}"

@mcp.tool()
async def get_weather_insights(location: str) -> str:
    """Get AI-powered weather insights and recommendations."""
    try:
        logger.info("Getting AI insights for: %s", location)
        
        weather_data = await weather_service.get_current_weather(location)
        forecast_data = await weather_service.get_forecast(location)
        
        insights = await ai_service.generate_weather_insights(
            weather_data, 
            forecast_data, 
            location
        )
        
        return f"Weather insights for {location}:\n{insights}"
        
    except Exception as e:
        logger.error("AI insights failed: %s", e)
        return f"Unable to generate insights for {location}: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
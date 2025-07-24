"""
OpenWeatherMap API service for retrieving weather forecast data.
Handles API calls, response parsing, and error handling.
"""
# services/weather_service.py
import logging
from typing import Dict, Any, List
import sys
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add parent directory to path for settings import
# sys.path.append(str(Path(__file__).parent.parent))
from services.key_vault_service import KeyVaultService
from config.settings import Settings


logger = logging.getLogger(__name__)

class WeatherService:
    """Professional weather service with settings-based configuration."""
    
    def __init__(self, key_vault_service: KeyVaultService):
        self.key_vault_service = key_vault_service
        self.base_url = Settings.OPENWEATHER_BASE_URL
        self.forecast_endpoint = Settings.OPENWEATHER_FORECAST_ENDPOINT
        self.api_key_secret_name = Settings.OPENWEATHER_API_KEY_SECRET
        self.timeout = Settings.API_TIMEOUT_SECONDS
        self._api_key: str = None
        self._session: requests.Session = None
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        if self._session is None:
            session = requests.Session()
            
            # Your proven retry strategy
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            self._session = session
            logger.info("HTTP session initialized with retry strategy")
            
        return self._session
    
    async def _get_api_key(self) -> str:
        """Get OpenWeather API key from Key Vault using settings."""
        if self._api_key is None:
            self._api_key = await self.key_vault_service.get_secret(self.api_key_secret_name)
        return self._api_key
    
    async def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather data for location."""
        try:
            api_key = await self._get_api_key()
            session = self._create_session()
            
            response = session.get(
                f"{self.base_url}/weather",
                params={
                    "q": location,
                    "appid": api_key,
                    "units": "metric"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "location": data["name"],
                "temp": round(data["main"]["temp"]),
                "feels_like": round(data["main"]["feels_like"]),
                "description": data["weather"][0]["description"].title(),
                "humidity": data["main"]["humidity"],
                "wind_speed": round(data["wind"]["speed"]),
                "wind_direction": data["wind"].get("deg", 0)
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error("OpenWeather API error for %s: %s", location, e)
            if e.response.status_code == 404:
                raise ValueError(f"Location '{location}' not found")
            raise RuntimeError(f"Weather service unavailable: {e.response.status_code}")
            
        except Exception as e:
            logger.error("Weather request failed for %s: %s", location, e)
            raise RuntimeError(f"Unable to get weather for {location}") from e
    
    async def get_forecast(self, location: str) -> List[Dict[str, Any]]:
        """Get 5-day forecast for location with proper daily aggregation."""
        try:
            api_key = await self._get_api_key()
            session = self._create_session()
            
            response = session.get(
                self.forecast_endpoint,
                params={
                    "q": location,
                    "appid": api_key,
                    "units": "metric"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Group by date first (like Azure Function does)
            daily_data = {}
            for item in data["list"]:
                forecast_date = item["dt_txt"].split()[0]
                if forecast_date not in daily_data:
                    daily_data[forecast_date] = []
                daily_data[forecast_date].append(item)
            
            # Aggregate daily min/max properly
            daily_forecasts = []
            for date, entries in sorted(daily_data.items()):
                if len(daily_forecasts) >= Settings.EXPECTED_FORECAST_DAYS:
                    break
                    
                # Find true daily min/max across all 3-hour periods
                temp_highs = [entry["main"]["temp_max"] for entry in entries]
                temp_lows = [entry["main"]["temp_min"] for entry in entries]
                descriptions = list(set(entry["weather"][0]["description"] for entry in entries))
                
                daily_forecasts.append({
                    "date": date,
                    "temp_high": round(max(temp_highs)),    # True daily maximum
                    "temp_low": round(min(temp_lows)),      # True daily minimum
                    "description": ", ".join(descriptions),
                    "humidity": entries[0]["main"]["humidity"],  # First entry for consistency
                    "wind_speed": round(entries[0]["wind"]["speed"])
                })
                    
            return daily_forecasts
                
        except Exception as e:
            logger.error("Forecast request failed for %s: %s", location, e)
            raise RuntimeError(f"Unable to get forecast for {location}") from e
"""
OpenAI API service for generating weather forecast narratives.
Handles AI prompt construction and response processing.
"""
# services/ai_service.py
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

class AIService:
    """Professional AI service with settings-based configuration."""
    
    def __init__(self, key_vault_service: KeyVaultService):
        self.key_vault_service = key_vault_service
        self.api_url = Settings.OPENAI_API_URL
        self.api_key_secret_name = Settings.OPENAI_API_KEY_SECRET
        self.model = Settings.OPENAI_MODEL
        self.max_tokens = Settings.OPENAI_MAX_COMPLETION_TOKENS
        self.temperature = Settings.OPENAI_TEMPERATURE
        self.timeout = Settings.API_TIMEOUT_SECONDS
        self._api_key: str = None
        self._session: requests.Session = None
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        if self._session is None:
            session = requests.Session()
            
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            self._session = session
            logger.info("AI service HTTP session initialized")
            
        return self._session
    
    async def _get_api_key(self) -> str:
        """Get OpenAI API key from Key Vault using settings."""
        if self._api_key is None:
            self._api_key = await self.key_vault_service.get_secret(self.api_key_secret_name)
        return self._api_key
    
    async def generate_weather_insights(
        self, 
        current_weather: Dict[str, Any], 
        forecast: List[Dict[str, Any]], 
        location: str
    ) -> str:
        """Generate AI-powered weather insights using settings configuration."""
        try:
            api_key = await self._get_api_key()
            session = self._create_session()
            
            # Prepare weather context
            weather_context = f"""
Current weather in {location}:
- Temperature: {current_weather['temp']}°C (feels like {current_weather['feels_like']}°C)
- Condition: {current_weather['description']}
- Humidity: {current_weather['humidity']}%
- Wind: {current_weather['wind_speed']} kph

5-day forecast:"""
            
            for day in forecast:
                weather_context += f"\n- {day['date']}: {day['temp_high']}°/{day['temp_low']}° - {day['description']}"
            
            response = session.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional meteorologist. Provide practical weather insights and recommendations based on the data."
                        },
                        {
                            "role": "user",
                            "content": f"Analyze this weather data and provide insights:\n{weather_context}"
                        }
                    ],
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
                
        except Exception as e:
            logger.error("AI insights generation failed: %s", e)
            return f"Weather analysis unavailable. Current conditions: {current_weather['temp']}°F, {current_weather['description']}"
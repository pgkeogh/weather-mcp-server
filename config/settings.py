"""
Application configuration and constants.
All environment variables and magic values centralized here.
"""
import os
from typing import Dict, Any


class Settings:
    """Application configuration loaded from environment variables."""
    
    # Azure Configuration
    KEY_VAULT_NAME: str = os.getenv("KEY_VAULT_NAME", "")
    #KEY_VAULT_NAME: str = "pgk-key-vault"
    
    # API Configuration
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    OPENWEATHER_FORECAST_ENDPOINT: str = f"{OPENWEATHER_BASE_URL}/forecast"
    
    # OpenAI Configuration
    OPENAI_API_URL: str = "https://api.openai.com/v1/chat/completions"
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_MAX_COMPLETION_TOKENS: int = int(os.getenv("OPENAI_MAX_COMPLETION_TOKENS", "1000"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "1.1"))
    
    # Key Vault Secret Names
    OPENWEATHER_API_KEY_SECRET: str = "OWM-API-KEY"
    OPENAI_API_KEY_SECRET: str = "OPENAI-API-KEY"
    
    # Request Configuration
    API_TIMEOUT_SECONDS: int = int(os.getenv("API_TIMEOUT_SECONDS", "30"))
    
    # Validation Constants
    MIN_LATITUDE: float = -90.0
    MAX_LATITUDE: float = 90.0
    MIN_LONGITUDE: float = -180.0
    MAX_LONGITUDE: float = 180.0
    
    # Forecast Configuration
    EXPECTED_FORECAST_DAYS: int = 5
    
    @classmethod
    def validate_required_settings(cls) -> None:
        """Validate that all required settings are present."""
        if not cls.KEY_VAULT_NAME:
            raise ValueError("KEY_VAULT_NAME environment variable is required")
    
    @classmethod
    def get_azure_credential_config(cls) -> Dict[str, bool]:
        """Get Azure credential configuration for managed identity."""
        return {
            "exclude_environment_credential": True,
            "exclude_managed_identity_credential": False,
            "exclude_shared_token_cache_credential": True,
            "exclude_visual_studio_code_credential": True,
            "exclude_cli_credential": True,
            "exclude_interactive_browser_credential": True,
            "exclude_powershell_credential": True,
            "exclude_developer_sign_on_credential": True,
            "exclude_visual_studio_credential": True,
            "exclude_azure_portal_credential": True,
        }


# Global settings instance
settings = Settings()

"""
Custom exception classes for the weather forecast application.
Provides specific error types for different failure scenarios.
"""


class WeatherForecastError(Exception):
    """Base exception for all weather forecast related errors."""
    pass


class ValidationError(WeatherForecastError):
    """Raised when input validation fails."""
    pass


class ConfigurationError(WeatherForecastError):
    """Raised when application configuration is invalid."""
    pass


class KeyVaultError(WeatherForecastError):
    """Raised when Azure Key Vault operations fail."""
    pass


class WeatherServiceError(WeatherForecastError):
    """Raised when weather service API calls fail."""
    pass


class AIServiceError(WeatherForecastError):
    """Raised when AI service API calls fail."""
    pass


class DataProcessingError(WeatherForecastError):
    """Raised when weather data processing fails."""
    pass
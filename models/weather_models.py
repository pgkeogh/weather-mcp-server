"""
Data models for weather forecast application.
Provides type-safe, validated data structures.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Optional, Any
import json


@dataclass(frozen=True)
class Location:
    """Represents a geographical location with coordinates."""
    latitude: float
    longitude: float
    
    def __post_init__(self):
        """Validate coordinates after initialization."""
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Invalid latitude: {self.latitude}. Must be between -90 and 90.")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Invalid longitude: {self.longitude}. Must be between -180 and 180.")


@dataclass
class WeatherCondition:
    """Represents weather conditions for a specific time period."""
    timestamp: datetime
    temperature: float
    temperature_min: float
    temperature_max: float
    description: str
    humidity: Optional[float] = None
    
    @property
    def date(self) -> date:
        """Get the date component of the timestamp."""
        return self.timestamp.date()


@dataclass
class DailyWeatherSummary:
    """Aggregated weather summary for a single day."""
    date: date
    max_temperature: float
    min_temperature: float
    weather_conditions: List[str]
    
    def __post_init__(self):
        """Validate data after initialization."""
        if self.max_temperature < self.min_temperature:
            raise ValueError(
                f"Max temperature ({self.max_temperature}) cannot be less than "
                f"min temperature ({self.min_temperature}) for {self.date}"
            )
        if not self.weather_conditions:
            raise ValueError(f"Weather conditions cannot be empty for {self.date}")
    
    @property
    def temperature_range(self) -> float:
        """Calculate the temperature range for the day."""
        return self.max_temperature - self.min_temperature
    
    @property
    def formatted_date(self) -> str:
        """Return date in YYYY-MM-DD format."""
        return self.date.strftime('%Y-%m-%d')
    
    
    # @property
    # def conditions_summary(self) -> str:
    #     """Return weather conditions as a comma-separated string."""
    #     return ', '.join(self.weather_conditions)

    @property
    def conditions_summary(self) -> str:
        """Returns weather conditions as readable string."""
        if not self.weather_conditions:
            return "unknown"
        
        # Remove duplicates while preserving order
        unique_conditions = []
        for condition in self.weather_conditions:
            if condition not in unique_conditions:
                unique_conditions.append(condition)
        
        if len(unique_conditions) == 1:
            return unique_conditions[0]
        elif len(unique_conditions) == 2:
            return f"{unique_conditions[0]} and {unique_conditions[1]}"
        else:
            return f"{', '.join(unique_conditions[:-1])}, and {unique_conditions[-1]}"
    
    def __str__(self) -> str:
        """Professional string representation."""
        return f"{self.formatted_date}: {self.min_temperature} - {self.max_temperature} ({self.conditions_summary})"
    
    
@dataclass
class WeatherForecastData:
    """Raw weather forecast data from the API."""
    location: Location
    forecast_conditions: List[WeatherCondition]
    retrieved_at: datetime = field(default_factory=datetime.now)
    
    def get_daily_summaries(self) -> List[DailyWeatherSummary]:
        """Convert raw conditions to daily summaries."""
        daily_data: Dict[date, List[WeatherCondition]] = {}
        
        # Group conditions by date
        for condition in self.forecast_conditions:
            condition_date = condition.date
            if condition_date not in daily_data:
                daily_data[condition_date] = []
            daily_data[condition_date].append(condition)
        
        # Create daily summaries
        summaries = []
        for forecast_date, conditions in sorted(daily_data.items()):
            max_temp = max(c.temperature_max for c in conditions)
            min_temp = min(c.temperature_min for c in conditions)
            descriptions = list(set(c.description for c in conditions))
            
            summary = DailyWeatherSummary(
                date=forecast_date,
                max_temperature=max_temp,
                min_temperature=min_temp,
                weather_conditions=descriptions
            )
            summaries.append(summary)
        
        return summaries[:5]


@dataclass
class WeatherForecast:
    """Complete weather forecast with AI-generated narrative."""
    location: Location
    daily_summaries: List[DailyWeatherSummary]
    ai_narrative: str
    style: str
    generated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate forecast data."""
        if len(self.daily_summaries) != 5:
            raise ValueError(f"Expected 5 daily summaries, got {len(self.daily_summaries)}")
        if not self.ai_narrative.strip():
            raise ValueError("AI narrative cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert forecast to dictionary for JSON serialization."""
        return {
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude
            },
            "forecast": [
                {
                    "date": summary.formatted_date,
                    "max_temperature": summary.max_temperature,
                    "min_temperature": summary.min_temperature,
                    "conditions": summary.weather_conditions,
                    "temperature_range": summary.temperature_range
                }
                for summary in self.daily_summaries
            ],
            "narrative": self.ai_narrative,
            "style": self.style,
            "generated_at": self.generated_at.isoformat()
        }
    
    def to_json(self) -> str:
        """Convert forecast to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
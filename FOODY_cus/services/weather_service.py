import requests
import json
from datetime import datetime

class WeatherService:
    def __init__(self, api_key=None):
        # Default to a free API that doesn't require authentication
        self.api_key = api_key
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        
    def get_current_weather(self, latitude=21.0245, longitude=105.8412):  # Default to Hanoi
        """Get current weather data for the specified location"""
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
            'timezone': 'auto'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            current = data.get('current', {})
            
            # Map weather code to description
            weather_code = current.get('weather_code', 0)
            weather_description = self._get_weather_description(weather_code)
            
            return {
                'temperature': current.get('temperature_2m', 0),
                'humidity': current.get('relative_humidity_2m', 0),
                'weather_description': weather_description,
                'wind_speed': current.get('wind_speed_10m', 0),
                'time_of_day': self._get_time_of_day(),
                'success': True
            }
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return {
                'temperature': 25,
                'humidity': 80,
                'weather_description': 'Sunny',
                'wind_speed': 5,
                'time_of_day': self._get_time_of_day(),
                'success': False,
                'error': str(e)
            }
    
    def _get_weather_description(self, code):
        """Map WMO weather codes to descriptions"""
        weather_codes = {
            0: 'Clear sky',
            1: 'Mainly clear',
            2: 'Partly cloudy',
            3: 'Overcast',
            45: 'Fog',
            48: 'Depositing rime fog',
            51: 'Light drizzle',
            53: 'Moderate drizzle',
            55: 'Dense drizzle',
            56: 'Light freezing drizzle',
            57: 'Dense freezing drizzle',
            61: 'Slight rain',
            63: 'Moderate rain',
            65: 'Heavy rain',
            66: 'Light freezing rain',
            67: 'Heavy freezing rain',
            71: 'Slight snow fall',
            73: 'Moderate snow fall',
            75: 'Heavy snow fall',
            77: 'Snow grains',
            80: 'Slight rain showers',
            81: 'Moderate rain showers',
            82: 'Violent rain showers',
            85: 'Slight snow showers',
            86: 'Heavy snow showers',
            95: 'Thunderstorm',
            96: 'Thunderstorm with slight hail',
            99: 'Thunderstorm with heavy hail'
        }
        return weather_codes.get(code, 'Unknown')
    
    def _get_time_of_day(self):
        """Get current time of day (morning, afternoon, evening, night)"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night' 
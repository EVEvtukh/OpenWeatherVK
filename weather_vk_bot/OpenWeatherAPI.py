"""Модуль для работы с OpenWeather API."""
import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL: str = os.getenv("WEATHER_API_BASE", "https://api.openweathermap.org/data/2.5")


class OpenWeatherAPI:
    """Клиент для OpenWeatherMap API."""

    @staticmethod
    def get_weather_by_city(city: str, extended: bool = False) -> dict:
        """Получает текущую погоду по названию города."""
        if not API_KEY:
            raise ValueError("Не задан OPENWEATHER_API_KEY в .env")
        
        url = f"{BASE_URL}/weather"
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",
            "lang": "ru",
        }
        
        logger.info(f"Запрос погоды для города: {city}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_forecast_by_city(city: str) -> dict:
        """Получает прогноз на 5 дней по названию города."""
        if not API_KEY:
            raise ValueError("Не задан OPENWEATHER_API_KEY в .env")
        
        url = f"{BASE_URL}/forecast"
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",
            "lang": "ru",
        }
        
        logger.info(f"Запрос прогноза для города: {city}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_weather_by_coordinates(lat: float, lon: float, extended: bool = False) -> dict:
        """Получает текущую погоду по координатам."""
        if not API_KEY:
            raise ValueError("Не задан OPENWEATHER_API_KEY в .env")
        
        url = f"{BASE_URL}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric",
            "lang": "ru",
        }
        
        logger.info(f"Запрос погоды по координатам: {lat}, {lon}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_air_quality(lat: float, lon: float) -> dict:
        """Получает данные о качестве воздуха по координатам."""
        if not API_KEY:
            raise ValueError("Не задан OPENWEATHER_API_KEY в .env")
        
        url = f"{BASE_URL}/air_pollution"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
        }
        
        logger.info(f"Запрос качества воздуха: {lat}, {lon}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

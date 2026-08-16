"""
openweather
===========

Production-ready OOP-модуль для работы с OpenWeatherMap API.

Поддерживаемые endpoint (только актуальные):
    - Current Weather   : /data/2.5/weather
    - 5 Day Forecast    : /data/2.5/forecast
    - Air Pollution     : /data/2.5/air_pollution
    - Direct Geocoding  : /geo/1.0/direct
    - Reverse Geocoding : /geo/1.0/reverse

Архитектура рассчитана на лёгкое расширение (UV Index, Historical, Alerts).
"""

from __future__ import annotations

from .api import OpenWeatherAPI
from .exceptions import APIConnectionError, CityNotFoundError, OpenWeatherAPIError
from .models import AirQualityResult

__all__ = [
    "OpenWeatherAPI",
    "AirQualityResult",
    "OpenWeatherAPIError",
    "CityNotFoundError",
    "APIConnectionError",
]

__version__ = "1.0.0"

"""
exceptions.py
=============

Кастомные исключения модуля OpenWeatherAPI.

Иерархия
--------
OpenWeatherAPIError (базовое)
├── CityNotFoundError
└── APIConnectionError
"""

from __future__ import annotations


class OpenWeatherAPIError(Exception):
    """Базовое исключение для всех ошибок модуля OpenWeatherAPI."""


class CityNotFoundError(OpenWeatherAPIError):
    """Город не найден при геокодировании (прямом или обратном)."""


class APIConnectionError(OpenWeatherAPIError):
    """Ошибка сетевого соединения с API OpenWeatherMap (таймаут, обрыв и т.п.)."""

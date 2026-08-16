"""
api.py
======

Основной класс ``OpenWeatherAPI`` — собирает воедино все миксины
(геокодирование, текущая погода, прогноз, загрязнение воздуха,
форматирование) и предоставляет публичные методы.

Архитектура рассчитана на лёгкое расширение (UV Index, Historical,
Alerts) — достаточно добавить новый миксин и подключить его сюда.
"""

from __future__ import annotations

from typing import Any, Dict

from .air_pollution import AirPollutionMixin
from .current_weather import CurrentWeatherMixin
from .exceptions import CityNotFoundError
from .forecast import ForecastMixin
from .formatters import FormattersMixin
from .geocoding import GeocodingMixin
from .http_client import BaseWeatherClient
from .models import AirQualityResult


class OpenWeatherAPI(
    BaseWeatherClient,
    GeocodingMixin,
    CurrentWeatherMixin,
    ForecastMixin,
    AirPollutionMixin,
    FormattersMixin,
):
    """
    Класс-обёртка над OpenWeatherMap API.

    Объединяет HTTP-клиент, геокодирование, погодные запросы,
    анализ качества воздуха и форматирование результатов.

    Публичные методы
    ----------------
    get_weather_by_city(city, extended=False)
    get_forecast_by_city(city, extended=False)
    get_weather_by_coordinates(lat, lon, extended=False)
    """

    # ==================================================================
    # Публичные методы
    # ==================================================================
    def get_weather_by_city(
        self, city: str, extended: bool = False
    ) -> Dict[str, Any]:
        """
        Получение текущей погоды по названию города.

        Параметры
        ---------
        city : str
            Название города (можно с кодом страны, напр. ``"Zocca,IT"``).
        extended : bool
            Если ``True`` — возвращаются дополнительные поля:
            sunrise, sunset, sea_level, grnd_level, visibility
            и полный анализ качества воздуха.

        Возвращает
        ----------
        dict
            Структурированные погодные данные.

        Исключения
        ----------
        CityNotFoundError
            Если город не найден.
        APIConnectionError
            При сетевой ошибке.
        OpenWeatherAPIError
            При прочих ошибках API.
        """
        geo: Dict[str, Any] = self._direct_geocode(city)
        lat: float = geo["lat"]
        lon: float = geo["lon"]

        weather: Dict[str, Any] = self._current_weather(lat, lon)

        if extended:
            air_data: Dict[str, Any] = self._air_pollution(lat, lon)
            air_result: AirQualityResult = self._analyze_air_quality(air_data)
            return self._format_extended_weather(weather, air_result)

        return self._format_basic_weather(weather)

    def get_forecast_by_city(
        self, city: str, extended: bool = False
    ) -> Dict[str, Any]:
        """
        Получение прогноза на 5 дней по названию города.

        Параметры
        ---------
        city : str
            Название города.
        extended : bool
            Включить sunrise / sunset города.

        Возвращает
        ----------
        dict
            Структурированный прогноз.

        Исключения
        ----------
        CityNotFoundError
            Если город не найден.
        """
        geo: Dict[str, Any] = self._direct_geocode(city)
        lat: float = geo["lat"]
        lon: float = geo["lon"]

        forecast: Dict[str, Any] = self._forecast_weather(lat, lon)
        return self._format_forecast_data(forecast, extended=extended)

    def get_weather_by_coordinates(
        self, lat: float, lon: float, extended: bool = False
    ) -> Dict[str, Any]:
        """
        Получение текущей погоды по координатам.

        Параметры
        ---------
        lat, lon : float
            Широта и долгота.
        extended : bool
            Возвращать расширенные данные + анализ воздуха.

        Возвращает
        ----------
        dict
            Структурированные погодные данные.
        """
        weather: Dict[str, Any] = self._current_weather(lat, lon)

        # Если в ответе нет названия города — пытаемся получить его
        # через обратное геокодирование
        if not weather.get("name") or weather.get("name") == "":
            try:
                geo: Dict[str, Any] = self._reverse_geocode(lat, lon)
                weather["name"] = geo.get("name", "—")
                if "sys" not in weather:
                    weather["sys"] = {}
                weather["sys"]["country"] = geo.get("country", "—")
            except CityNotFoundError:
                pass

        if extended:
            air_data: Dict[str, Any] = self._air_pollution(lat, lon)
            air_result: AirQualityResult = self._analyze_air_quality(air_data)
            return self._format_extended_weather(weather, air_result)

        return self._format_basic_weather(weather)

    # ==================================================================
    # Точка расширения для будущих endpoint
    # ==================================================================
    # def get_uv_index(self, lat: float, lon: float) -> Dict[str, Any]:
    #     """Будущая реализация: UV Index API."""
    #     raise NotImplementedError
    #
    # def get_historical(self, lat: float, lon: float, dt: int) -> Dict[str, Any]:
    #     """Будущая реализация: Historical API."""
    #     raise NotImplementedError
    #
    # def get_alerts(self, lat: float, lon: float) -> Dict[str, Any]:
    #     """Будущая реализация: Weather Alerts."""
    #     raise NotImplementedError

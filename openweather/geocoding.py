"""
geocoding.py
============

Миксин геокодирования: прямой (город → координаты) и обратный
(координаты → город) геокодинг через endpoint'ы ``/geo/1.0/direct``
и ``/geo/1.0/reverse``.
"""

from __future__ import annotations

from typing import Any, Dict

from .constants import ENDPOINT_DIRECT_GEOCODE, ENDPOINT_REVERSE_GEOCODE
from .exceptions import CityNotFoundError


class GeocodingMixin:
    """Миксин прямого и обратного геокодирования."""

    # ==================================================================
    # Прямое геокодирование
    # ==================================================================
    def _direct_geocode(self, city: str) -> Dict[str, Any]:
        """
        Прямое геокодирование: название города → координаты.

        Параметры
        ---------
        city : str
            Название города (можно с кодом страны, напр. ``"London,GB"``).

        Возвращает
        ----------
        dict
            Первый совпавший результат геокодирования.

        Исключения
        ----------
        CityNotFoundError
            Если город не найден.
        APIConnectionError
            При сетевой ошибке.
        OpenWeatherAPIError
            При некорректном ответе API.
        """
        params: Dict[str, Any] = {
            "q": city,
            "limit": 1,
            "appid": self.api_key,
        }
        data = self._make_request(ENDPOINT_DIRECT_GEOCODE, params)

        if not data or not isinstance(data, list) or len(data) == 0:
            raise CityNotFoundError(f"Город '{city}' не найден.")

        return data[0]

    # ==================================================================
    # Обратное геокодирование
    # ==================================================================
    def _reverse_geocode(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Обратное геокодирование: координаты → название города.

        Параметры
        ---------
        lat, lon : float
            Широта и долгота.

        Возвращает
        ----------
        dict
            Первый результат обратного геокодирования.

        Исключения
        ----------
        CityNotFoundError
            Если по координатам не найдено населённого пункта.
        APIConnectionError
            При сетевой ошибке.
        """
        params: Dict[str, Any] = {
            "lat": lat,
            "lon": lon,
            "limit": 1,
            "appid": self.api_key,
        }
        data = self._make_request(ENDPOINT_REVERSE_GEOCODE, params)

        if not data or not isinstance(data, list) or len(data) == 0:
            raise CityNotFoundError(
                f"Населённый пункт для координат ({lat}, {lon}) не найден."
            )

        return data[0]

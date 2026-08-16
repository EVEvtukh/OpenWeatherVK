"""
current_weather.py
==================

Миксин текущей погоды. Обращается к endpoint ``/data/2.5/weather``.
"""

from __future__ import annotations

from typing import Any, Dict

from .constants import ENDPOINT_CURRENT_WEATHER


class CurrentWeatherMixin:
    """Миксин запроса текущей погоды по координатам."""

    def _current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Запрос текущей погоды по координатам.

        Параметры
        ---------
        lat, lon : float
            Широта и долгота.

        Возвращает
        ----------
        dict
            JSON-ответ endpoint ``/data/2.5/weather``.
        """
        params: Dict[str, Any] = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": self.units,
            "lang": self.lang,
        }
        return self._make_request(ENDPOINT_CURRENT_WEATHER, params)

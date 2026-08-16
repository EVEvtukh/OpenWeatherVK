"""
forecast.py
===========

Миксин прогноза погоды на 5 дней. Обращается к endpoint
``/data/2.5/forecast``.
"""

from __future__ import annotations

from typing import Any, Dict

from .constants import ENDPOINT_FORECAST


class ForecastMixin:
    """Миксин запроса прогноза погоды по координатам."""

    def _forecast_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Запрос прогноза на 5 дней по координатам.

        Параметры
        ---------
        lat, lon : float
            Широта и долгота.

        Возвращает
        ----------
        dict
            JSON-ответ endpoint ``/data/2.5/forecast``.
        """
        params: Dict[str, Any] = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": self.units,
            "lang": self.lang,
        }
        return self._make_request(ENDPOINT_FORECAST, params)

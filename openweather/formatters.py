"""
formatters.py
=============

Миксин форматирования погодных данных: базовая и расширенная
текущая погода, а также прогноз на 5 дней.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import AirQualityResult


class FormattersMixin:
    """Миксин форматирования сырых JSON-ответов в структурированный вид."""

    # ==================================================================
    # Базовое форматирование текущей погоды
    # ==================================================================
    def _format_basic_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Форматирование базовой информации о текущей погоде.

        Параметры
        ---------
        data : dict
            JSON-ответ ``/data/2.5/weather``.

        Возвращает
        ----------
        dict
            Базовый словарь погодных данных.
        """
        weather_list: List[Dict[str, Any]] = data.get("weather", [{}])
        weather_main: str = weather_list[0].get("main", "—") if weather_list else "—"
        weather_desc: str = (
            weather_list[0].get("description", "—") if weather_list else "—"
        )

        main: Dict[str, Any] = data.get("main", {})
        wind: Dict[str, Any] = data.get("wind", {})
        clouds: Dict[str, Any] = data.get("clouds", {})
        sys: Dict[str, Any] = data.get("sys", {})

        return {
            "city": data.get("name", "—"),
            "country": sys.get("country", "—"),
            "weather_main": weather_main,
            "weather_description": weather_desc,
            "temperature": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "temp_min": main.get("temp_min"),
            "temp_max": main.get("temp_max"),
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
            "wind_speed": wind.get("speed"),
            "clouds": clouds.get("all"),
        }

    # ==================================================================
    # Расширенное форматирование текущей погоды
    # ==================================================================
    def _format_extended_weather(
        self, data: Dict[str, Any], air_result: Optional[AirQualityResult] = None
    ) -> Dict[str, Any]:
        """
        Форматирование расширенной информации о текущей погоде.

        Параметры
        ---------
        data : dict
            JSON-ответ ``/data/2.5/weather``.
        air_result : AirQualityResult, optional
            Результат анализа качества воздуха.

        Возвращает
        ----------
        dict
            Расширенный словарь погодных данных.
        """
        base: Dict[str, Any] = self._format_basic_weather(data)

        main: Dict[str, Any] = data.get("main", {})
        sys: Dict[str, Any] = data.get("sys", {})

        extended: Dict[str, Any] = {
            **base,
            "sunrise": sys.get("sunrise"),
            "sunset": sys.get("sunset"),
            "sea_level": main.get("sea_level"),
            "grnd_level": main.get("grnd_level"),
            "visibility": data.get("visibility"),
        }

        if air_result is not None:
            extended["air_quality"] = {
                "aqi_index": air_result.aqi_index,
                "aqi_label": air_result.aqi_label,
                "pollutant_details": air_result.pollutant_details,
                "exceeded_pollutants": air_result.exceeded_pollutants,
                "human_summary": air_result.human_summary,
            }

        return extended

    # ==================================================================
    # Форматирование прогноза
    # ==================================================================
    def _format_forecast_data(
        self, data: Dict[str, Any], extended: bool = False
    ) -> Dict[str, Any]:
        """
        Форматирование данных прогноза на 5 дней.

        Параметры
        ---------
        data : dict
            JSON-ответ ``/data/2.5/forecast``.
        extended : bool
            Включать ли дополнительные поля (sunrise, sunset).

        Возвращает
        ----------
        dict
            Структурированный прогноз.
        """
        city: Dict[str, Any] = data.get("city", {})
        forecast_list: List[Dict[str, Any]] = data.get("list", [])

        items: List[Dict[str, Any]] = []
        for entry in forecast_list:
            weather_list: List[Dict[str, Any]] = entry.get("weather", [{}])
            main: Dict[str, Any] = entry.get("main", {})
            wind: Dict[str, Any] = entry.get("wind", {})
            clouds: Dict[str, Any] = entry.get("clouds", {})

            item: Dict[str, Any] = {
                "datetime": entry.get("dt_txt"),
                "temperature": main.get("temp"),
                "humidity": main.get("humidity"),
                "pressure": main.get("pressure"),
                "weather_description": (
                    weather_list[0].get("description", "—")
                    if weather_list
                    else "—"
                ),
                "clouds": clouds.get("all"),
                "wind_speed": wind.get("speed"),
                "pop": entry.get("pop"),
            }
            items.append(item)

        result: Dict[str, Any] = {
            "city": city.get("name", "—"),
            "country": city.get("country", "—"),
            "forecast": items,
        }

        if extended:
            result["sunrise"] = city.get("sunrise")
            result["sunset"] = city.get("sunset")

        return result

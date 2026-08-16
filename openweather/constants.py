"""
constants.py
============

Константы модуля OpenWeatherAPI: URL endpoint'ов, шкала качества
воздуха, человекочитаемые названия загрязнителей и маппинги AQI.

Используются только актуальные endpoint OpenWeatherMap.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Базовые URL
# ---------------------------------------------------------------------------
BASE_WEATHER_URL: str = "https://api.openweathermap.org/data/2.5"
BASE_GEO_URL: str = "http://api.openweathermap.org/geo/1.0"

# ---------------------------------------------------------------------------
# Endpoint'ы (только указанные в ТЗ)
# ---------------------------------------------------------------------------
ENDPOINT_CURRENT_WEATHER: str = f"{BASE_WEATHER_URL}/weather"
ENDPOINT_FORECAST: str = f"{BASE_WEATHER_URL}/forecast"
ENDPOINT_AIR_POLLUTION: str = f"{BASE_WEATHER_URL}/air_pollution"
ENDPOINT_DIRECT_GEOCODE: str = f"{BASE_GEO_URL}/direct"
ENDPOINT_REVERSE_GEOCODE: str = f"{BASE_GEO_URL}/reverse"

# ---------------------------------------------------------------------------
# Шкала качества воздуха
# ---------------------------------------------------------------------------
# Формат: {pollutant: [(верхняя_граница, лейбл), ...]}
# Значения упорядочены по возрастанию; последнее — "Very Poor".
AQ_SCALE: Dict[str, List[Tuple[float, str]]] = {
    "so2": [
        (20.0, "Good"),
        (80.0, "Fair"),
        (250.0, "Moderate"),
        (350.0, "Poor"),
        (float("inf"), "Very Poor"),
    ],
    "no2": [
        (40.0, "Good"),
        (70.0, "Fair"),
        (150.0, "Moderate"),
        (200.0, "Poor"),
        (float("inf"), "Very Poor"),
    ],
    "pm10": [
        (20.0, "Good"),
        (50.0, "Fair"),
        (100.0, "Moderate"),
        (200.0, "Poor"),
        (float("inf"), "Very Poor"),
    ],
    "pm2_5": [
        (10.0, "Good"),
        (25.0, "Fair"),
        (50.0, "Moderate"),
        (75.0, "Poor"),
        (float("inf"), "Very Poor"),
    ],
    "o3": [
        (60.0, "Good"),
        (100.0, "Fair"),
        (140.0, "Moderate"),
        (180.0, "Poor"),
        (float("inf"), "Very Poor"),
    ],
    "co": [
        (4400.0, "Good"),
        (9400.0, "Fair"),
        (12400.0, "Moderate"),
        (15400.0, "Poor"),
        (float("inf"), "Very Poor"),
    ],
}

# Человекочитаемые названия загрязнителей (рус.)
POLLUTANT_LABELS_RU: Dict[str, str] = {
    "co": "CO (угарный газ)",
    "no2": "NO2 (диоксид азота)",
    "o3": "O3 (озон)",
    "so2": "SO2 (диоксид серы)",
    "pm2_5": "PM2.5 (мелкие частицы)",
    "pm10": "PM10 (крупные частицы)",
}

# ---------------------------------------------------------------------------
# Маппинги AQI
# ---------------------------------------------------------------------------
# Шкала AQI → рус. описание
AQI_LABELS_RU: Dict[int, str] = {
    1: "Хорошее",
    2: "Приемлемое",
    3: "Умеренное",
    4: "Плохое",
    5: "Очень плохое",
}

# Шкала AQI → англ. описание
AQI_LABELS_EN: Dict[int, str] = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor",
}

# Ранг «худшести» лейбла для определения итогового уровня
AQI_RANK: Dict[str, int] = {
    "Good": 1,
    "Fair": 2,
    "Moderate": 3,
    "Poor": 4,
    "Very Poor": 5,
}

# Маппинг англ. лейбл → рус. лейбл
AQI_LABEL_EN_TO_RU: Dict[str, str] = {
    "Good": "Хорошее",
    "Fair": "Приемлемое",
    "Moderate": "Умеренное",
    "Poor": "Плохое",
    "Very Poor": "Очень плохое",
}

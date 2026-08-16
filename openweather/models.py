"""
models.py
=========

Дата-классы (структуры данных), используемые для возврата
результатов анализа из модуля OpenWeatherAPI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AirQualityResult:
    """
    Структурированный результат анализа качества воздуха.

    Атрибуты
    --------
    aqi_index : Optional[int]
        Числовой индекс AQI (из API либо вычисленный ранг).
    aqi_label : str
        Текстовая метка качества воздуха на русском.
    pollutant_details : Dict[str, float]
        Значения концентраций по каждому загрязнителю.
    human_summary : str
        Человекочитаемое описание качества воздуха.
    exceeded_pollutants : List[str]
        Список загрязнителей, вышедших за уровень «Good».
    """
    aqi_index: Optional[int]
    aqi_label: str
    pollutant_details: Dict[str, float]
    human_summary: str
    exceeded_pollutants: List[str] = field(default_factory=list)

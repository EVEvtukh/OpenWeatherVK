"""
air_pollution.py
================

Миксин загрязнения воздуха. Обращается к endpoint
``/data/2.5/air_pollution`` и содержит аналитический метод
``_analyze_air_quality`` с человекочитаемым выводом.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .constants import (
    AQI_LABEL_EN_TO_RU,
    AQI_RANK,
    AQ_SCALE,
    ENDPOINT_AIR_POLLUTION,
    POLLUTANT_LABELS_RU,
)
from .models import AirQualityResult


class AirPollutionMixin:
    """Миксин запроса и анализа данных о загрязнении воздуха."""

    # ==================================================================
    # Запрос данных о загрязнении
    # ==================================================================
    def _air_pollution(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Запрос данных о загрязнении воздуха по координатам.

        Параметры
        ---------
        lat, lon : float
            Широта и долгота.

        Возвращает
        ----------
        dict
            JSON-ответ endpoint ``/data/2.5/air_pollution``.
        """
        params: Dict[str, Any] = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
        }
        return self._make_request(ENDPOINT_AIR_POLLUTION, params)

    # ==================================================================
    # Анализ качества воздуха
    # ==================================================================
    def _analyze_air_quality(self, air_data: Dict[str, Any]) -> AirQualityResult:
        """
        Аналитический метод, формирующий человекочитаемый вывод
        о качестве воздуха на основе компонентов загрязнения.

        Логика
        ------
        Для каждого загрязнителя определяется уровень по шкале
        (Good / Fair / Moderate / Poor / Very Poor). Итоговый AQI-лейбл
        выбирается как **наихудший** среди всех компонентов. Если API
        возвращает собственный ``aqi``, он используется как ``aqi_index``.

        Параметры
        ---------
        air_data : dict
            JSON-ответ endpoint ``/data/2.5/air_pollution``.

        Возвращает
        ----------
        AirQualityResult
            Структурированный результат с индексом, лейблом,
            деталями по загрязнителям и человекочитаемым описанием.
        """
        if not air_data or "list" not in air_data or len(air_data["list"]) == 0:
            return AirQualityResult(
                aqi_index=None,
                aqi_label="Недоступно",
                pollutant_details={},
                human_summary="Данные о качестве воздуха недоступны.",
            )

        entry: Dict[str, Any] = air_data["list"][0]
        components: Dict[str, float] = entry.get("components", {})
        api_aqi: Optional[int] = entry.get("main", {}).get("aqi")

        # Детали по каждому загрязнителю
        pollutant_details: Dict[str, float] = {}
        per_pollutant_labels: Dict[str, str] = {}
        exceeded_pollutants: List[str] = []

        worst_label: str = "Good"

        for pollutant, value in components.items():
            pollutant_details[pollutant] = value

            scale = AQ_SCALE.get(pollutant)
            if scale is None:
                continue

            # Определяем уровень для данного загрязнителя
            label = "Very Poor"
            for upper, lvl in scale:
                if value < upper:
                    label = lvl
                    break

            per_pollutant_labels[pollutant] = label

            # Обновляем наихудший лейбл
            if AQI_RANK.get(label, 0) > AQI_RANK.get(worst_label, 0):
                worst_label = label

            # Загрязнители, вышедшие за «Good»
            if label != "Good":
                exceeded_pollutants.append(pollutant)

        # Итоговый лейбл
        aqi_label_en: str = worst_label
        aqi_label_ru: str = AQI_LABEL_EN_TO_RU.get(aqi_label_en, "Неизвестно")

        # Человекочитаемое описание
        human_summary: str = self._build_air_summary(
            aqi_label_en, aqi_label_ru, exceeded_pollutants, per_pollutant_labels
        )

        # Индекс AQI: если API вернул — используем его,
        # иначе вычисляем ранг наихудшего лейбла
        aqi_index: Optional[int] = (
            api_aqi if api_aqi is not None else AQI_RANK.get(aqi_label_en)
        )

        return AirQualityResult(
            aqi_index=aqi_index,
            aqi_label=aqi_label_ru,
            pollutant_details=pollutant_details,
            human_summary=human_summary,
            exceeded_pollutants=exceeded_pollutants,
        )

    # ------------------------------------------------------------------
    # Вспомогательный метод формирования summary
    # ------------------------------------------------------------------
    def _build_air_summary(
        self,
        label_en: str,
        label_ru: str,
        exceeded: List[str],
        per_labels: Dict[str, str],
    ) -> str:
        """
        Формирование человекочитаемого summary качества воздуха.

        Параметры
        ---------
        label_en : str
            Итоговый лейбл (англ.).
        label_ru : str
            Итоговый лейбл (рус.).
        exceeded : list[str]
            Список загрязнителей, вышедших за «Good».
        per_labels : dict
            Лейблы по каждому загрязнителю.

        Возвращает
        ----------
        str
            Готовое текстовое описание.
        """
        # Базовые фразы по уровням
        base_phrases: Dict[str, str] = {
            "Good": "Качество воздуха — Хорошее. Все основные загрязнители в пределах безопасной нормы.",
            "Fair": "Качество воздуха — Приемлемое.",
            "Moderate": "Качество воздуха — Умеренное.",
            "Poor": "Качество воздуха — Плохое. Людям с чувствительностью следует ограничить пребывание на улице.",
            "Very Poor": "Качество воздуха — Очень плохое. Высокий риск для здоровья.",
        }

        summary: str = base_phrases.get(label_en, "Качество воздуха не определено.")

        # Дополнение: конкретные загрязнители
        if exceeded:
            details: List[str] = []
            for pollutant in exceeded:
                ru_name = POLLUTANT_LABELS_RU.get(pollutant, pollutant)
                lvl_ru = AQI_LABEL_EN_TO_RU.get(per_labels.get(pollutant, ""), "Неизвестно")
                details.append(f"{ru_name} — уровень «{lvl_ru}»")

            if label_en == "Fair":
                summary += " Слегка повышены: " + "; ".join(details) + "."
            elif label_en in ("Moderate", "Poor", "Very Poor"):
                summary += " Превышают норму: " + "; ".join(details) + "."

        return summary

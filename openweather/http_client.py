"""
http_client.py
==============

Базовый HTTP-клиент модуля OpenWeatherAPI.

Содержит конструктор, инициализацию сессии ``requests.Session``
и низкоуровневый метод ``_make_request`` с обработкой ошибок.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

from .exceptions import APIConnectionError, CityNotFoundError, OpenWeatherAPIError

# Загрузка переменных окружения из .env (если файл присутствует)
load_dotenv()


class BaseWeatherClient:
    """
    Базовый HTTP-клиент для OpenWeatherMap API.

    Атрибуты
    --------
    api_key : str
        Ключ API OpenWeatherMap.
    session : requests.Session
        Переиспользуемая HTTP-сессия.
    units : str
        Единицы измерения (metric / imperial / standard).
    lang : str
        Язык текстовых описаний погоды (ru, en и т.д.).
    timeout : float
        Таймаут HTTP-запроса в секундах.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        units: str = "metric",
        lang: str = "ru",
        timeout: float = 15.0,
    ) -> None:
        """
        Инициализация клиента OpenWeatherMap.

        Параметры
        ---------
        api_key : str, optional
            Ключ API. Если не указан, берётся из переменной окружения
            ``OPENWEATHER_API_KEY``.
        units : str
            Единицы измерения температуры
            (``metric``, ``imperial``, ``standard``).
        lang : str
            Язык описаний погоды.
        timeout : float
            Таймаут HTTP-запроса в секундах.
        """
        self.api_key: str = api_key or os.getenv("OPENWEATHER_API_KEY", "")
        if not self.api_key:
            raise OpenWeatherAPIError(
                "API ключ не предоставлен. Укажите его через параметр "
                "api_key или переменную окружения OPENWEATHER_API_KEY."
            )

        self.units: str = units
        self.lang: str = lang
        self.timeout: float = timeout

        self.session: requests.Session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    # ==================================================================
    # Низкоуровневый HTTP-запрос
    # ==================================================================
    def _make_request(self, url: str, params: Dict[str, Any]) -> Any:
        """
        Выполнение HTTP GET-запроса к API с обработкой ошибок.

        Параметры
        ---------
        url : str
            URL endpoint.
        params : dict
            Параметры запроса.

        Возвращает
        ----------
        Any
            Распарсенный JSON-ответ (dict или list).

        Исключения
        ----------
        APIConnectionError
            При сетевой ошибке или таймауте.
        OpenWeatherAPIError
            При HTTP-ошибке или некорректном JSON.
        CityNotFoundError
            При коде 404 от API геокодирования.
        """
        try:
            response = self.session.get(
                url, params=params, timeout=self.timeout
            )
        except requests.exceptions.Timeout as exc:
            raise APIConnectionError(
                f"Превышен таймаут запроса к {url}."
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise APIConnectionError(
                f"Ошибка соединения с {url}: {exc}"
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise APIConnectionError(
                f"Ошибка запроса к {url}: {exc}"
            ) from exc

        # Обработка HTTP-статусов
        if response.status_code == 404:
            raise CityNotFoundError(
                "Ресурс не найден (404). Проверьте название города или координаты."
            )
        if response.status_code == 401:
            raise OpenWeatherAPIError(
                "Неавторизованный доступ (401). Проверьте API-ключ."
            )
        if response.status_code == 429:
            raise OpenWeatherAPIError(
                "Превышен лимит запросов (429). Попробуйте позже."
            )
        if not response.ok:
            raise OpenWeatherAPIError(
                f"Ошибка API: HTTP {response.status_code} — {response.text}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise OpenWeatherAPIError(
                f"Некорректный JSON-ответ от {url}: {exc}"
            ) from exc

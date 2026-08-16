"""
main.py
=======

Точка входа в приложение OpenWeatherAPI.

Демонстрирует использование модуля ``openweather``:
    - текущая погода по городу (базовая и расширенная);
    - прогноз на 5 дней;
    - текущая погода по координатам;
    - анализ качества воздуха.

Для работы создайте файл ``.env`` рядом с ``main.py``:
    OPENWEATHER_API_KEY=ваш_ключ

Запуск:
    python main.py
"""

from __future__ import annotations

import json
import sys
from typing import Any

# Принудительная установка UTF-8 для корректного вывода кириллицы в Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from openweather import (
    APIConnectionError,
    CityNotFoundError,
    OpenWeatherAPI,
    OpenWeatherAPIError,
)


def _print_result(title: str, data: Any) -> None:
    """Красивый вывод результата в консоль.

    Параметры
    ---------
    title : str
        Заголовок выводимого блока.
    data : Any
        Данные для вывода (будут сериализованы в JSON).
    """
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> int:
    """
    Основная функция точки входа.

    Возвращает
    ----------
    int
        Код завершения (0 — успех, 1 — ошибка).
    """
    try:
        client = OpenWeatherAPI()
    except OpenWeatherAPIError as exc:
        print(f"Ошибка инициализации клиента: {exc}", file=sys.stderr)
        print(
            "Создайте файл .env с переменной OPENWEATHER_API_KEY=ваш_ключ",
            file=sys.stderr,
        )
        return 1

    # Демо-город (можно переопределить аргументом командной строки)
    city: str = sys.argv[1] if len(sys.argv) > 1 else "Zocca,IT"

    try:
        # 1. Базовая текущая погода по городу
        basic = client.get_weather_by_city(city)
        _print_result(f"Текущая погода (базово): {city}", basic)

        # 2. Расширенная текущая погода + анализ воздуха
        extended = client.get_weather_by_city(city, extended=True)
        _print_result(f"Текущая погода (расширенно): {city}", extended)

        # 3. Прогноз на 5 дней (расширенный)
        forecast = client.get_forecast_by_city(city, extended=True)
        _print_result(f"Прогноз на 5 дней: {city}", forecast)

        # 4. Погода по координатам (если известны)
        if "air_quality" in extended:
            lat = 44.34  # координаты Zocca как пример
            lon = 10.99
            by_coords = client.get_weather_by_coordinates(lat, lon, extended=True)
            _print_result(f"Погода по координатам ({lat}, {lon})", by_coords)

    except CityNotFoundError as exc:
        print(f"Город не найден: {exc}", file=sys.stderr)
        return 1
    except APIConnectionError as exc:
        print(f"Ошибка соединения: {exc}", file=sys.stderr)
        return 1
    except OpenWeatherAPIError as exc:
        print(f"Ошибка API: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

.\.venv\Scripts\Activate.ps1
pip install -r weather_vk_bot\requirements.txt
python weather_vk_bot\main.py
..\..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
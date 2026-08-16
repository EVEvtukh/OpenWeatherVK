"""
cli.py
======

Модуль командной строки (CLI) для OpenWeatherAPI.

Два режима работы:
    1. Интерактивный (по умолчанию) — запускается без аргументов,
       показывает меню для выбора действия и ввода данных.
    2. Прямой — через аргументы командной строки (для скриптов).

Интерактивный режим
-------------------
    python cli.py

Прямой режим
------------
    # Текущая погода по городу (базово)
    python cli.py weather --city "Zocca,IT"

    # Текущая погода по городу (расширенно + анализ воздуха)
    python cli.py weather --city "Zocca,IT" --extended

    # Текущая погода по координатам (расширенно)
    python cli.py weather --lat 44.34 --lon 10.99 --extended

    # Прогноз на 5 дней
    python cli.py forecast --city "Zocca,IT"

    # Прогноз на 5 дней (расширенно: sunrise/sunset)
    python cli.py forecast --city "Zocca,IT" --extended

    # Компактный вывод в одну строку
    python cli.py weather --city "Zocca,IT" --compact
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Optional, Tuple

# Принудительная установка UTF-8 для корректного ввода/вывода кириллицы в Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")

from openweather import (
    APIConnectionError,
    CityNotFoundError,
    OpenWeatherAPI,
    OpenWeatherAPIError,
)


# ===========================================================================
# Парсер аргументов (прямой режим)
# ===========================================================================
def build_parser() -> argparse.ArgumentParser:
    """
    Построение парсера аргументов командной строки.

    Возвращает
    ----------
    ArgumentParser
        Настроенный парсер CLI.
    """
    # Общие опции, наследуемые всеми субпарсерами
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--compact",
        action="store_true",
        help="Компактный вывод в одну строку (только ключевые поля)",
    )
    common_parser.add_argument(
        "--units",
        choices=["metric", "imperial", "standard"],
        default="metric",
        help="Единицы измерения (по умолчанию: metric)",
    )
    common_parser.add_argument(
        "--lang",
        default="ru",
        help="Язык описаний погоды (по умолчанию: ru)",
    )

    parser = argparse.ArgumentParser(
        prog="openweather-cli",
        description="CLI-клиент для OpenWeatherMap API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Примеры:\n"
            '  python cli.py weather --city "Zocca,IT"\n'
            '  python cli.py weather --city "Zocca,IT" --extended\n'
            "  python cli.py weather --lat 44.34 --lon 10.99 --extended\n"
            '  python cli.py forecast --city "Zocca,IT" --extended\n'
            "\nИнтерактивный режим (без аргументов):\n"
            "  python cli.py"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command", required=False, help="Доступные команды"
    )

    # --- Команда: weather (текущая погода) ---
    weather_parser = subparsers.add_parser(
        "weather",
        parents=[common_parser],
        help="Текущая погода по городу или координатам",
    )
    _add_location_args(weather_parser)
    weather_parser.add_argument(
        "-e", "--extended",
        action="store_true",
        help="Расширенный вывод: sunrise, sunset, visibility, анализ воздуха",
    )

    # --- Команда: forecast (прогноз на 5 дней) ---
    forecast_parser = subparsers.add_parser(
        "forecast",
        parents=[common_parser],
        help="Прогноз на 5 дней по городу или координатам",
    )
    _add_location_args(forecast_parser)
    forecast_parser.add_argument(
        "-e", "--extended",
        action="store_true",
        help="Добавить sunrise / sunset города",
    )

    return parser


def _add_location_args(subparser: argparse.ArgumentParser) -> None:
    """
    Добавление аргументов локации (город или координаты) в субпарсер.

    Параметры
    ---------
    subparser : ArgumentParser
        Субпарсер, в который добавляются аргументы.
    """
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--city",
        type=str,
        help='Название города (напр. "Zocca,IT" или "London,GB")',
    )
    group.add_argument(
        "--lat",
        type=float,
        help="Широта (используется вместе с --lon)",
    )
    subparser.add_argument(
        "--lon",
        type=float,
        help="Долгота (используется вместе с --lat)",
    )


# ===========================================================================
# Форматирование вывода
# ===========================================================================
def _format_compact(data: Dict[str, Any], command: str) -> str:
    """
    Компактный однострочный вывод ключевых данных.

    Параметры
    ---------
    data : dict
        Результат API-запроса.
    command : str
        Тип команды ("weather" или "forecast").

    Возвращает
    ----------
    str
        Строка компактного вывода.
    """
    if command == "weather":
        city = data.get("city", "—")
        temp = data.get("temperature", "—")
        desc = data.get("weather_description", "—")
        feels = data.get("feels_like", "—")
        humidity = data.get("humidity", "—")
        wind = data.get("wind_speed", "—")
        return (
            f"{city}: {desc}, {temp}°C "
            f"(ощущается {feels}°C), влажность {humidity}%, ветер {wind} м/с"
        )

    # forecast
    city = data.get("city", "—")
    count = len(data.get("forecast", []))
    return f"{city}: прогноз на {count} интервалов (5 дней)"


def _print_result(data: Dict[str, Any], command: str, compact: bool) -> None:
    """
    Вывод результата запроса в консоль.

    Параметры
    ---------
    data : dict
        Результат API-запроса.
    command : str
        Тип команды ("weather" или "forecast").
    compact : bool
        Если True — компактный однострочный вывод.
    """
    if compact:
        print(_format_compact(data, command))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


# ===========================================================================
# Общая логика запросов (используется обоими режимами)
# ===========================================================================
def fetch_weather(
    client: OpenWeatherAPI,
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    extended: bool = False,
) -> Dict[str, Any]:
    """
    Получение текущей погоды.

    Параметры
    ---------
    client : OpenWeatherAPI
        Экземпляр клиента API.
    city : str, optional
        Название города.
    lat, lon : float, optional
        Координаты.
    extended : bool
        Расширенный вывод.

    Возвращает
    ----------
    dict
        Результат запроса погоды.
    """
    if city:
        return client.get_weather_by_city(city, extended=extended)
    if lat is not None and lon is not None:
        return client.get_weather_by_coordinates(lat, lon, extended=extended)
    raise OpenWeatherAPIError("Необходимо указать город либо координаты.")


def fetch_forecast(
    client: OpenWeatherAPI,
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    extended: bool = False,
) -> Dict[str, Any]:
    """
    Получение прогноза на 5 дней.

    Параметры
    ---------
    client : OpenWeatherAPI
        Экземпляр клиента API.
    city : str, optional
        Название города.
    lat, lon : float, optional
        Координаты.
    extended : bool
        Добавить sunrise / sunset.

    Возвращает
    ----------
    dict
        Результат запроса прогноза.
    """
    if city:
        return client.get_forecast_by_city(city, extended=extended)
    if lat is not None and lon is not None:
        forecast_raw = client._forecast_weather(lat, lon)
        return client._format_forecast_data(forecast_raw, extended=extended)
    raise OpenWeatherAPIError("Необходимо указать город либо координаты.")


# ===========================================================================
# Обработчики команд для прямого режима (argparse)
# ===========================================================================
def cmd_weather(client: OpenWeatherAPI, args: argparse.Namespace) -> Dict[str, Any]:
    """
    Обработка команды ``weather`` — текущая погода (прямой режим).

    Параметры
    ---------
    client : OpenWeatherAPI
        Экземпляр клиента API.
    args : Namespace
        Распарсенные аргументы CLI.

    Возвращает
    ----------
    dict
        Результат запроса погоды.
    """
    return fetch_weather(
        client, city=args.city, lat=args.lat, lon=args.lon, extended=args.extended
    )


def cmd_forecast(client: OpenWeatherAPI, args: argparse.Namespace) -> Dict[str, Any]:
    """
    Обработка команды ``forecast`` — прогноз на 5 дней (прямой режим).

    Параметры
    ---------
    client : OpenWeatherAPI
        Экземпляр клиента API.
    args : Namespace
        Распарсенные аргументы CLI.

    Возвращает
    ----------
    dict
        Результат запроса прогноза.
    """
    return fetch_forecast(
        client, city=args.city, lat=args.lat, lon=args.lon, extended=args.extended
    )


# ===========================================================================
# Интерактивный режим
# ===========================================================================
def _input(prompt: str, default: str = "") -> str:
    """
    Безопасный ввод с поддержкой значения по умолчанию.

    Параметры
    ---------
    prompt : str
        Текст приглашения.
    default : str
        Значение по умолчанию (если пользователь нажал Enter).

    Возвращает
    ----------
    str
        Введённое значение.
    """
    try:
        # Явный сброс буфера, чтобы промпт отобразился до блокировки на ввод
        sys.stdout.write(prompt)
        sys.stdout.flush()
        raw = input().strip()
    except EOFError:
        print()
        return default
    return raw if raw else default


def _input_float(prompt: str) -> Optional[float]:
    """
    Ввод числа с плавающей точкой с валидацией.

    Параметры
    ---------
    prompt : str
        Текст приглашения.

    Возвращает
    ----------
    Optional[float]
        Введённое число или None при ошибке ввода.
    """
    try:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        raw = input().strip()
    except EOFError:
        print()
        return None
    if not raw:
        return None
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        print(f"  [!] Некорректное число: '{raw}'")
        return None


def _choose_location() -> Tuple[Optional[str], Optional[float], Optional[float]]:
    """
    Интерактивный выбор локации: город или координаты.

    Возвращает
    ----------
    tuple
        (city, lat, lon) — один из вариантов будет заполнен.
    """
    print("\n--- Выбор локации ---")
    print("  1. По названию города")
    print("  2. По координатам (широта, долгота)")
    choice = _input("\nВаш выбор [1]: ", "1")

    if choice == "2":
        lat = _input_float("  Широта (lat): ")
        lon = _input_float("  Долгота (lon): ")
        if lat is None or lon is None:
            print("  [!] Координаты не указаны корректно.")
            return None, None, None
        return None, lat, lon
    else:
        city = _input("  Название города (напр. Zocca,IT или London,GB): ")
        if not city:
            print("  [!] Город не указан.")
            return None, None, None
        return city, None, None


def _run_interactive(client: OpenWeatherAPI) -> int:
    """
    Главный цикл интерактивного меню.

    Параметры
    ---------
    client : OpenWeatherAPI
        Экземпляр клиента API.

    Возвращает
    ----------
    int
        Код завершения (0 — успех).
    """
    while True:
        print("\n" + "=" * 50)
        print("   OpenWeatherMap CLI — Интерактивный режим")
        print("=" * 50)
        print("  1. Текущая погода (базовая)")
        print("  2. Текущая погода (расширенная + анализ воздуха)")
        print("  3. Прогноз на 5 дней (базовый)")
        print("  4. Прогноз на 5 дней (расширенный: sunrise/sunset)")
        print("  0. Выход")

        choice = _input("\nВаш выбор: ", "0")

        if choice == "0":
            print("\nДо свидания!")
            return 0

        # Маппинг выбора → (команда, extended)
        commands: Dict[str, Tuple[str, bool]] = {
            "1": ("weather", False),
            "2": ("weather", True),
            "3": ("forecast", False),
            "4": ("forecast", True),
        }

        if choice not in commands:
            print("  [!] Неверный выбор. Попробуйте снова.")
            continue

        command, extended = commands[choice]

        # Выбор локации
        city, lat, lon = _choose_location()
        if city is None and lat is None:
            continue

        # Выбор формата вывода
        print("\n--- Формат вывода ---")
        print("  1. Подробный (JSON)")
        print("  2. Компактный (одна строка)")
        fmt = _input("Ваш выбор [1]: ", "1")
        compact = fmt == "2"

        # Выполнение запроса
        print("\nЗапрашиваю данные...")
        try:
            if command == "weather":
                result = fetch_weather(
                    client, city=city, lat=lat, lon=lon, extended=extended
                )
            else:
                result = fetch_forecast(
                    client, city=city, lat=lat, lon=lon, extended=extended
                )
        except CityNotFoundError as exc:
            print(f"\n[!] Город не найден: {exc}")
            continue
        except APIConnectionError as exc:
            print(f"\n[!] Ошибка соединения: {exc}")
            continue
        except OpenWeatherAPIError as exc:
            print(f"\n[!] Ошибка API: {exc}")
            continue

        # Вывод результата
        print("\n" + "-" * 50)
        _print_result(result, command, compact)
        print("-" * 50)

        # Продолжить или выйти
        again = _input("\nПродолжить? (y/n) [y]: ", "y")
        if again.lower() not in ("y", "yes", "д", "да", ""):
            print("\nДо свидания!")
            return 0


# ===========================================================================
# Точка входа
# ===========================================================================
def main(argv: Optional[list[str]] = None) -> int:
    """
    Главная функция CLI.

    Если аргументы не переданы — запускается интерактивный режим.
    Если переданы — работает прямой режим через argparse.

    Параметры
    ---------
    argv : list[str], optional
        Аргументы командной строки. Если ``None`` — берутся из ``sys.argv``.

    Возвращает
    ----------
    int
        Код завершения (0 — успех, 1 — ошибка).
    """
    # Определение, переданы ли аргументы команды
    raw_argv = argv if argv is not None else sys.argv[1:]
    has_command = len(raw_argv) > 0 and raw_argv[0] in ("weather", "forecast")

    # --- Интерактивный режим (без аргументов) ---
    if not has_command:
        try:
            client = OpenWeatherAPI()
        except OpenWeatherAPIError as exc:
            print(f"Ошибка инициализации клиента: {exc}", file=sys.stderr)
            print(
                "Создайте файл .env с переменной OPENWEATHER_API_KEY=ваш_ключ",
                file=sys.stderr,
            )
            return 1
        return _run_interactive(client)

    # --- Прямой режим (argparse) ---
    parser = build_parser()
    args = parser.parse_args(raw_argv)

    if args.command is None:
        try:
            client = OpenWeatherAPI()
        except OpenWeatherAPIError as exc:
            print(f"Ошибка инициализации клиента: {exc}", file=sys.stderr)
            return 1
        return _run_interactive(client)

    # Валидация: если указан --lat без --lon (и наоборот)
    if args.lat is not None and args.lon is None:
        parser.error("--lat требует также --lon")
    if args.lon is not None and args.lat is None:
        parser.error("--lon требует также --lat")

    # Инициализация клиента
    try:
        client = OpenWeatherAPI(units=args.units, lang=args.lang)
    except OpenWeatherAPIError as exc:
        print(f"Ошибка инициализации клиента: {exc}", file=sys.stderr)
        print(
            "Создайте файл .env с переменной OPENWEATHER_API_KEY=ваш_ключ",
            file=sys.stderr,
        )
        return 1

    # Выполнение команды
    try:
        if args.command == "weather":
            result = cmd_weather(client, args)
        elif args.command == "forecast":
            result = cmd_forecast(client, args)
        else:
            parser.error(f"Неизвестная команда: {args.command}")
            return 1
    except CityNotFoundError as exc:
        print(f"Город не найден: {exc}", file=sys.stderr)
        return 1
    except APIConnectionError as exc:
        print(f"Ошибка соединения: {exc}", file=sys.stderr)
        return 1
    except OpenWeatherAPIError as exc:
        print(f"Ошибка API: {exc}", file=sys.stderr)
        return 1

    # Вывод результата
    _print_result(result, args.command, args.compact)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

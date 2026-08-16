"""Связующее звено между VKBottle и OpenWeatherAPI."""
import logging
import requests
from typing import Optional

from OpenWeatherAPI import OpenWeatherAPI
from services.formatter import format_current_weather, format_forecast

logger = logging.getLogger(__name__)


class WeatherService:
    """Сервис для получения и обработки погодных данных."""

    @staticmethod
    def get_current_weather(city: str, extended: bool = False) -> str:
        """Получает и форматирует текущую погоду."""
        try:
            data = OpenWeatherAPI.get_weather_by_city(city, extended)
            return format_current_weather(data, extended)
        except ValueError as e:
            logger.error(f"Ошибка конфигурации: {e}")
            return "⚠️ Ошибка конфигурации бота. Попробуйте позже."
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            if status == 404:
                return f"🏙 Город \"{city}\" не найден.\nВведите название города на русском или английском."
            elif status == 401:
                return "⚠️ Ошибка авторизации API. Обратитесь к администратору."
            elif status == 429:
                return "⏳ Слишком много запросов. Подождите минуту и попробуйте снова."
            return f"❌ Ошибка API (статус {status}). Попробуйте позже."
        except requests.exceptions.Timeout:
            return "⏰ Превышено время ожидания ответа от сервера погоды."
        except requests.exceptions.ConnectionError:
            return "🔌 Не удалось подключиться к серверу погоды. Проверьте интернет."
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при получении погоды для {city}")
            return f"❌ Произошла ошибка: {str(e)}"

    @staticmethod
    def get_forecast(city: str) -> str:
        """Получает и форматирует прогноз на 5 дней."""
        try:
            data = OpenWeatherAPI.get_forecast_by_city(city)
            return format_forecast(data)
        except ValueError as e:
            logger.error(f"Ошибка конфигурации: {e}")
            return "⚠️ Ошибка конфигурации бота. Попробуйте позже."
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            if status == 404:
                return f"🏙 Город \"{city}\" не найден.\nВведите название города."
            elif status == 401:
                return "⚠️ Ошибка авторизации API. Обратитесь к администратору."
            elif status == 429:
                return "⏳ Слишком много запросов. Подождите минуту."
            return f"❌ Ошибка API (статус {status}). Попробуйте позже."
        except requests.exceptions.Timeout:
            return "⏰ Превышено время ожидания ответа от сервера погоды."
        except requests.exceptions.ConnectionError:
            return "🔌 Не удалось подключиться к серверу погоды."
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при получении прогноза для {city}")
            return f"❌ Произошла ошибка: {str(e)}"

    @staticmethod
    def get_weather_by_geo(lat: float, lon: float, extended: bool = False) -> str:
        """Получает погоду по координатам."""
        try:
            data = OpenWeatherAPI.get_weather_by_coordinates(lat, lon, extended)
            return format_current_weather(data, extended)
        except ValueError as e:
            logger.error(f"Ошибка конфигурации: {e}")
            return "⚠️ Ошибка конфигурации бота. Попробуйте позже."
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            if status == 401:
                return "⚠️ Ошибка авторизации API."
            return f"❌ Ошибка API (статус {status})."
        except requests.exceptions.Timeout:
            return "⏰ Превышено время ожидания ответа."
        except requests.exceptions.ConnectionError:
            return "🔌 Не удалось подключиться к серверу погоды."
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при получении погоды по координатам")
            return f"❌ Произошла ошибка: {str(e)}"

    @staticmethod
    def parse_coordinates(text: str) -> Optional[tuple]:
        """Парсит координаты из строки."""
        text = text.strip().replace(",", " ").replace(";", " ")
        parts = text.split()
        
        # Фильтруем только числовые значения
        nums = []
        for part in parts:
            try:
                nums.append(float(part))
            except ValueError:
                continue
        
        if len(nums) >= 2:
            lat, lon = nums[0], nums[1]
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return (lat, lon)
        
        return None

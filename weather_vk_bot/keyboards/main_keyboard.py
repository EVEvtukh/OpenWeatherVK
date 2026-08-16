"""Основные клавиатуры главного меню."""
from vkbottle import Keyboard, KeyboardButtonColor, Text


def get_main_keyboard() -> str:
    """Возвращает JSON главной клавиатуры."""
    keyboard = (
        Keyboard(one_time=False, inline=False)
        .add(Text("🌤 Погода сейчас", payload={"cmd": "weather_now"}),
             color=KeyboardButtonColor.PRIMARY)
        .add(Text("📅 Прогноз 5 дней", payload={"cmd": "forecast"}),
             color=KeyboardButtonColor.SECONDARY)
        .row()
        .add(Text("📍 Геолокация", payload={"cmd": "geo"}),
             color=KeyboardButtonColor.POSITIVE)
        .add(Text("🌫 Расширенный режим", payload={"cmd": "extended"}),
             color=KeyboardButtonColor.SECONDARY)
        .row()
        .add(Text("ℹ️ Помощь", payload={"cmd": "help"}),
             color=KeyboardButtonColor.SECONDARY)
    )
    return keyboard.get_json()


def get_back_keyboard() -> str:
    """Возвращает клавиатуру с кнопкой возврата."""
    keyboard = (
        Keyboard(one_time=False, inline=False)
        .add(Text("🏠 Главное меню", payload={"cmd": "main"}),
             color=KeyboardButtonColor.SECONDARY)
    )
    return keyboard.get_json()

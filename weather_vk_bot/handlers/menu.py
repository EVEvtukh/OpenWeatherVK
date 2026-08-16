"""Хендлеры главного меню."""
import logging
from vkbottle.bot import Message, BotLabeler

from config import bot
from keyboards.main_keyboard import get_main_keyboard
from services.state_manager import WeatherStates

logger = logging.getLogger(__name__)

menu_labeler = BotLabeler()


@menu_labeler.message(text=["начать", "start"])
async def start_handler(message: Message):
    """Обработка команды 'начать' — первое сообщение."""
    await bot.state_dispenser.set(
        peer_id=message.peer_id,
        state=WeatherStates.MAIN,
    )
    await message.answer(
        "👋 Добро пожаловать в погодного бота!\n\n"
        "Я могу показать текущую погоду, прогноз на 5 дней,\n"
        "погоду по геолокации и качество воздуха.\n\n"
        "Выберите действие из меню ниже 👇",
        keyboard=get_main_keyboard(),
    )


@menu_labeler.message(payload={"cmd": "weather_now"})
async def weather_now(message: Message):
    """Обработка запроса текущей погоды — переход к вводу города."""
    await bot.state_dispenser.set(
        peer_id=message.peer_id,
        state=WeatherStates.WAITING_CITY,
    )
    await message.answer(
        "🌤 Введите название города для получения текущей погоды:\n"
        "Пример: Москва, London, New York",
        keyboard=get_main_keyboard(),
    )


@menu_labeler.message(payload={"cmd": "forecast"})
async def forecast_request(message: Message):
    """Обработка запроса прогноза — переход к вводу города."""
    await bot.state_dispenser.set(
        peer_id=message.peer_id,
        state=WeatherStates.WAITING_FORECAST_CITY,
    )
    await message.answer(
        "📅 Введите название города для получения прогноза на 5 дней:",
        keyboard=get_main_keyboard(),
    )


@menu_labeler.message(payload={"cmd": "geo"})
async def geo_request(message: Message):
    """Обработка запроса погоды по геолокации."""
    await bot.state_dispenser.set(
        peer_id=message.peer_id,
        state=WeatherStates.WAITING_GEO,
    )
    await message.answer(
        "📍 Отправьте вашу геолокацию:\n\n"
        "💡 Нажмите 📍 в поле ввода сообщения и выберите «Геолокация»\n"
        "Или введите координаты вручную: 55.7558, 37.6173",
        keyboard=get_main_keyboard(),
    )


@menu_labeler.message(payload={"cmd": "extended"})
async def extended_request(message: Message):
    """Обработка запроса расширенной погоды с данными о воздухе."""
    await bot.state_dispenser.set(
        peer_id=message.peer_id,
        state=WeatherStates.WAITING_EXTENDED,
    )
    await message.answer(
        "🌫 Расширенный режим — погода + качество воздуха.\n\n"
        "Введите название города:",
        keyboard=get_main_keyboard(),
    )


@menu_labeler.message(payload={"cmd": "help"})
async def help_request(message: Message):
    """Обработка запроса помощи."""
    separator = "─" * 30
    await message.answer(
        f"ℹ️ Помощь\n"
        f"{separator}\n\n"
        f"Этот бот предоставляет актуальную погоду и прогноз.\n\n"
        f"🌤 Погода сейчас — текущая температура, влажность, ветер\n"
        f"📅 Прогноз 5 дней — прогноз на ближайшую неделю\n"
        f"📍 Геолокация — погода по вашему местоположению\n"
        f"🌫 Расширенный режим — погода + качество воздуха\n"
        f"ℹ️ Помощь — это сообщение\n\n"
        f"Совет: можно вводить города на русском или английском.\n"
        f"Пример: Москва, London, Tokyo",
        keyboard=get_main_keyboard(),
    )


@menu_labeler.message(payload={"cmd": "main"})
async def back_to_main(message: Message):
    """Возврат в главное меню."""
    await bot.state_dispenser.set(
        peer_id=message.peer_id,
        state=WeatherStates.MAIN,
    )
    await message.answer(
        "🏠 Главное меню",
        keyboard=get_main_keyboard(),
    )


@menu_labeler.message(payload={"cmd": "cancel"})
async def cancel_handler(message: Message):
    """Отмена текущего действия и возврат в главное меню."""
    await bot.state_dispenser.set(
        peer_id=message.peer_id,
        state=WeatherStates.MAIN,
    )
    await message.answer(
        "❌ Действие отменено.\n\nВыберите действие из меню 👇",
        keyboard=get_main_keyboard(),
    )

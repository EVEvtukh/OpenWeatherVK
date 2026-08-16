"""Главный хендлер — обработка текстовых сообщений по состоянию."""
import logging
from vkbottle.bot import Message, BotLabeler

from config import bot
from keyboards.main_keyboard import get_main_keyboard
from keyboards.navigation_keyboard import get_back_to_main_keyboard
from services.state_manager import WeatherStates
from services.weather_service import WeatherService

logger = logging.getLogger(__name__)

text_labeler = BotLabeler()
text_labeler.vbml_ignore_case = True


@text_labeler.message(text="ping")
async def ping_handler(message: Message):
    """Проверка работоспособности бота."""
    await message.answer("pong 🏓", keyboard=get_main_keyboard())


@text_labeler.message()
async def text_handler(message: Message):
    """Единый хендлер для всех текстовых сообщений — маршрутизация по состоянию."""
    state_peer = await bot.state_dispenser.get(peer_id=message.peer_id)
    text = message.text.strip() if message.text else ""

    # --- Нет состояния или MAIN → показываем главное меню ---
    if not state_peer or state_peer.state == WeatherStates.MAIN:
        await message.answer(
            "Выберите действие из меню 👇",
            keyboard=get_main_keyboard(),
        )
        return

    # --- Ввод координат вручную / геолокация ---
    if state_peer.state == WeatherStates.WAITING_GEO:
        lat, lon = 0, 0

        # Проверяем, есть ли в сообщении geo-вложение
        raw = getattr(message, "raw", None)
        if raw:
            geo = raw.get("geo") or raw.get("place")
            if geo:
                lat = float(geo.get("lat") or geo.get("latitude", 0))
                lon = float(geo.get("lng") or geo.get("lon") or geo.get("longitude", 0))

        if lat == 0 and lon == 0:
            # Пробуем распарсить текст как координаты
            coords = WeatherService.parse_coordinates(text)
            if coords:
                lat, lon = coords
            else:
                await message.answer(
                    "⚠️ Не удалось распознать координаты.\n\n"
                    "Введите координаты в формате: 55.7558, 37.6173",
                    keyboard=get_back_to_main_keyboard(),
                )
                return

        result = WeatherService.get_weather_by_geo(lat, lon)
        await message.answer(result, keyboard=get_main_keyboard())
        await bot.state_dispenser.set(
            peer_id=message.peer_id, state=WeatherStates.MAIN,
        )
        return

    # --- Ввод города для текущей погоды ---
    if state_peer.state == WeatherStates.WAITING_CITY:
        if not text:
            await message.answer(
                "⚠️ Вы не ввели название города.\nПожалуйста, введите название города:",
                keyboard=get_back_to_main_keyboard(),
            )
            return

        result = WeatherService.get_current_weather(text, extended=False)
        await message.answer(result, keyboard=get_main_keyboard())
        await bot.state_dispenser.set(
            peer_id=message.peer_id, state=WeatherStates.MAIN,
        )
        return

    # --- Ввод города для прогноза ---
    if state_peer.state == WeatherStates.WAITING_FORECAST_CITY:
        if not text:
            await message.answer(
                "⚠️ Вы не ввели название города.\nПожалуйста, введите название города:",
                keyboard=get_back_to_main_keyboard(),
            )
            return

        result = WeatherService.get_forecast(text)
        await message.answer(result, keyboard=get_main_keyboard())
        await bot.state_dispenser.set(
            peer_id=message.peer_id, state=WeatherStates.MAIN,
        )
        return

    # --- Ввод города для расширенного режима ---
    if state_peer.state == WeatherStates.WAITING_EXTENDED:
        if not text:
            await message.answer(
                "⚠️ Вы не ввели название города.\nПожалуйста, введите название города:",
                keyboard=get_back_to_main_keyboard(),
            )
            return

        result = WeatherService.get_current_weather(text, extended=True)
        await message.answer(result, keyboard=get_main_keyboard())
        await bot.state_dispenser.set(
            peer_id=message.peer_id, state=WeatherStates.MAIN,
        )
        return

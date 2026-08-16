"""Управление FSM-состояниями пользователя."""
from vkbottle.dispatch.dispenser.base import BaseStateGroup


class WeatherStates(BaseStateGroup):
    """Группа состояний для погодного бота."""
    
    MAIN = "main"
    WAITING_CITY = "waiting_city"
    WAITING_FORECAST_CITY = "waiting_forecast_city"
    WAITING_GEO = "waiting_geo"
    WAITING_EXTENDED = "waiting_extended"


def get_current_state_name(state_value: str) -> str:
    """Возвращает человеко-читаемое название текущего состояния."""
    if not state_value:
        return "Главное меню"
    
    state_map = {
        "waiting_city": "Ввод города для текущей погоды",
        "waiting_forecast_city": "Ввод города для прогноза",
        "waiting_geo": "Ожидание геолокации",
        "waiting_extended": "Ввод города для расширенной погоды",
    }
    return state_map.get(state_value, "Неизвестное состояние")

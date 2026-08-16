"""Навигационные клавиатуры."""
from vkbottle import Keyboard, KeyboardButtonColor, Text


def get_back_to_main_keyboard() -> str:
    """Возвращает клавиатуру с кнопкой возврата в главное меню."""
    keyboard = (
        Keyboard(one_time=False, inline=False)
        .add(Text("🏠 Главное меню", payload={"cmd": "main"}),
             color=KeyboardButtonColor.SECONDARY)
    )
    return keyboard.get_json()


def get_cancel_keyboard() -> str:
    """Возвращает клавиатуру с кнопкой отмены."""
    keyboard = (
        Keyboard(one_time=False, inline=False)
        .add(Text("❌ Отмена", payload={"cmd": "cancel"}),
             color=KeyboardButtonColor.NEGATIVE)
        .row()
        .add(Text("🏠 Главное меню", payload={"cmd": "main"}),
             color=KeyboardButtonColor.SECONDARY)
    )
    return keyboard.get_json()

"""Инициализация бота и регистрация хендлеров."""
from config import bot

# Загрузка всех хендлеров в глобальный лейблер.
# Порядок важен: конкретные декораторы → общие catch-all.
from handlers import (  # noqa: E402
    menu_labeler,
    text_labeler,
)

bot.labeler.load(menu_labeler)
bot.labeler.load(text_labeler)
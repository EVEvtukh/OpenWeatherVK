"""Точка входа в приложение VK Weather Bot."""
import logging

from bot import bot

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        logger.info("Запуск VK Weather Bot...")
        bot.run()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")

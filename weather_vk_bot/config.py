import os
from pathlib import Path
from dotenv import load_dotenv
from vkbottle import API, BuiltinStateDispenser, Bot
from vkbottle.bot import BotLabeler

# Загрузка .env из директории этого файла
_env_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=str(_env_dir / '.env'))

# Токены
VK_BOT_TOKEN: str = os.environ.get('VK_BOT_TOKEN', '')
OPENWEATHER_API_KEY: str = os.environ.get('OPENWEATHER_API_KEY', '')

if not VK_BOT_TOKEN:
    raise ValueError('VK_BOT_TOKEN not set in .env')
if not OPENWEATHER_API_KEY:
    raise ValueError('OPENWEATHER_API_KEY not set in .env')

# API
api: API = API(VK_BOT_TOKEN)

# Лейблер и диспенсер состояний
labeler: BotLabeler = BotLabeler()
state_dispenser: BuiltinStateDispenser = BuiltinStateDispenser()

# Бот
bot: Bot = Bot(
    api=api,
    labeler=labeler,
    state_dispenser=state_dispenser,
)

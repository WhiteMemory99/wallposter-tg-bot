from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from app import config


storage = RedisStorage2(
    host=config.REDIS_HOST,
    password=config.REDIS_PASSWORD
)

bot = Bot(
    token=config.BOT_TOKEN,
    parse_mode=types.ParseMode.HTML
)

dp = Dispatcher(
    bot=bot,
    storage=storage
)

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from app import config, handlers, middlewares, models
from app.services import logger, scheduler

storage = RedisStorage2(config.REDIS_HOST, password=config.REDIS_PASSWORD, prefix="wallposter")
bot = Bot(config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)


async def startup(dispatcher: Dispatcher):
    logger.setup("DEBUG" if config.DEBUG else "INFO")
    await models.setup(config.DB_URI)
    scheduler.setup()

    middlewares.setup(dispatcher, debug=config.DEBUG)
    handlers.setup(dispatcher)


async def shutdown(_):
    scheduler.shutdown()
    await models.shutdown()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown)

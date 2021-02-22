import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from app import config, handlers, middlewares, models
from app.services import logger, scheduler


async def main():
    storage = RedisStorage2(config.REDIS_HOST, password=config.REDIS_PASSWORD, prefix="wallposter")
    bot = Bot(config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
    dispatcher = Dispatcher(bot, storage=storage)

    logger.setup("DEBUG" if config.DEBUG else "INFO")
    await models.setup(config.DB_URI)
    scheduler.setup()
    middlewares.setup(dispatcher, debug=config.DEBUG)
    handlers.setup(dispatcher)

    try:
        await dispatcher.skip_updates()
        await dispatcher.start_polling()
    finally:
        scheduler.shutdown()
        await models.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

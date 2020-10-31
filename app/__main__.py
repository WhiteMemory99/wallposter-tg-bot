from aiogram import Dispatcher, executor

from app import config, handlers, middlewares, models
from app.misc import dp
from app.services import scheduler


async def startup_actions(dispatcher: Dispatcher):
    await models.setup(config.DB_URI)
    scheduler.setup()
    middlewares.setup(dispatcher)
    handlers.setup(dispatcher)


async def shutdown_actions(_):
    scheduler.shutdown()
    await models.shutdown()


if __name__ == '__main__':
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=startup_actions,
        on_shutdown=shutdown_actions
    )

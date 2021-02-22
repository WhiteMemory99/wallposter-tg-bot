from aiogram import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from app.middlewares.database import DBMiddleware


def setup(dispatcher: Dispatcher, debug: bool = False):
    dispatcher.middleware.setup(DBMiddleware())

    if debug:
        dispatcher.middleware.setup(LoggingMiddleware())

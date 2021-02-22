from aiogram import Dispatcher

from app.handlers import callback, error, user


def setup(dispatcher: Dispatcher):
    error.setup(dispatcher)
    user.setup(dispatcher)
    callback.setup(dispatcher)

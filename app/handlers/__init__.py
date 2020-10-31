from aiogram import Dispatcher

from app.handlers import callback, user


def setup(dispatcher: Dispatcher):
    user.setup(dispatcher)
    callback.setup(dispatcher)

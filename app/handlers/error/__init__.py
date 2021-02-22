from aiogram import Dispatcher
from aiogram.utils.exceptions import BotKicked, MessageNotModified

from app.handlers.error import errors


def setup(dp: Dispatcher):
    dp.register_errors_handler(errors.bot_kicked, exception=BotKicked)
    dp.register_errors_handler(errors.message_not_modified, exception=MessageNotModified)
    dp.register_errors_handler(errors.generic_error)

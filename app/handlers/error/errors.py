from aiogram import types
from loguru import logger

from app.models import Channel, Link


async def bot_kicked(update: types.Update, _):
    error_text = "Бот был удалён из канала, либо канала больше не существует."
    if update.message:
        await update.message.answer(error_text)
    elif update.callback_query:
        await update.callback_query.answer(error_text, show_alert=True)

    user = update.message.from_user if update.message else update.callback_query.from_user
    link = await Link.query.where(Link.user_id == user.id).gino.first()
    if link:
        await Channel.delete.where(Channel.id == link.channel_id).gino.status()

    return True


async def message_not_modified(update: types.Update, _):
    if update.callback_query:
        await update.callback_query.answer()

    return True


async def generic_error(_, exception: Exception):
    logger.exception(exception)
    return True

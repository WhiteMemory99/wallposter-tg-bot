from typing import Union

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from app.models import Link, User


class DBMiddleware(BaseMiddleware):
    @staticmethod
    async def setup_user(user: types.User, data: dict):
        user_data = await User.get(user.id)
        if user_data is None:
            user_data = await User.create(id=user.id)

        data["user"] = user_data

    @staticmethod
    async def setup_link(event: Union[types.Message, types.CallbackQuery], user: types.User, data: dict):
        link_data = await Link.query.where(Link.user_id == user.id).gino.first()
        if link_data is None:
            link_data = await Link.create(user_id=user.id, channel_id=None)

        if isinstance(event, types.CallbackQuery) and link_data.channel_id is None:
            await event.message.delete_reply_markup()
            await event.answer("Подключённый канал был удалён из моей базы данных.", show_alert=True)

            raise CancelHandler()

        data["link"] = link_data

    async def on_process_message(self, message: types.Message, data: dict):
        await self.setup_user(message.from_user, data)
        await self.setup_link(message, message.from_user, data)

    async def on_process_callback_query(self, query: types.Message, data: dict):
        await self.setup_user(query.from_user, data)
        await self.setup_link(query, query.from_user, data)

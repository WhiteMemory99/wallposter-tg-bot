from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from app.models.user import User


class ACLMiddleware(BaseMiddleware):
    @staticmethod
    async def setup_user(user: types.User, data: dict):
        user_data = await User.get(user.id)
        if user_data is None:
            user_data = await User.create(id=user.id)

        data["user"] = user_data

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.setup_user(message.from_user, data)

    async def on_pre_process_callback_query(self, call: types.Message, data: dict):
        await self.setup_user(call.from_user, data)

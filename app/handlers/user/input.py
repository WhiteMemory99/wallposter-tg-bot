from aiogram import types
from aiogram.dispatcher import FSMContext

from app.models import User
from app.utils import helper


async def new_title(message: types.Message, user: User, state: FSMContext):
    if not message.text:
        await message.answer('Введите текст до <b>100</b> символов.')
    elif len(message.text) > 100:
        await message.answer('Введите <b>до 100</b> символов.')
    else:
        data = await state.get_data()
        await state.reset_state()
        await user.update(sign_text=message.html_text).apply()

        text, markup = helper.get_settings_data(user)
        await message.answer(text, reply_markup=markup)
        await message.bot.edit_message_reply_markup(message.from_user.id, data['message_id'])


async def new_counter(message: types.Message, user: User, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer('Введите число <b>от 0 до 1000000</b>.')
    elif int(message.text) not in range(0, 1000001):
        await message.answer('Число должно быть <b>от 0 до 1000000</b>.')
    else:
        data = await state.get_data()
        await state.reset_state()
        await user.update(counter=int(message.text)).apply()

        text, markup = helper.get_settings_data(user)
        await message.answer(text, reply_markup=markup)
        await message.bot.edit_message_reply_markup(message.from_user.id, data['message_id'])

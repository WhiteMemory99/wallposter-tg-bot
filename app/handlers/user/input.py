from aiogram import types
from aiogram.dispatcher import FSMContext

from app.models import Channel, Link
from app.utils import helper

TEXT_LENGTH_LIMIT = 250


async def edit_signature(message: types.Message, state: FSMContext, link: Link):
    if not link.channel_id:
        await message.answer("Подключённый канал был удалён из бота.")
        await state.finish()
    elif not message.text or len(message.text) > TEXT_LENGTH_LIMIT:
        await message.answer(f"Введите текст до <b>{TEXT_LENGTH_LIMIT}</b> символов.")
    else:
        await state.finish()
        await Channel.update.values(signature_text=message.html_text).where(
            Channel.id == link.channel_id
        ).gino.status()

        chat = await message.bot.get_chat(link.channel_id)
        text, markup = await helper.get_settings_data(chat, link.channel_id, message.from_user.id)

        await message.answer(text, reply_markup=markup, disable_web_page_preview=True)


async def edit_counter_value(message: types.Message, state: FSMContext, link: Link):
    error_text = "Введите число от <b>0</b> до <b>100000000</b>."
    if not link.channel_id:
        await message.answer("Подключённый канал был удалён из бота.")
        await state.finish()
    elif not message.text or not message.text.isdigit():
        await message.answer(error_text)
    elif int(message.text) not in range(0, 100000001):
        await message.answer(error_text)
    else:
        await state.finish()
        await Channel.update.values(counter_value=int(message.text)).where(Channel.id == link.channel_id).gino.status()
        chat = await message.bot.get_chat(link.channel_id)
        text, markup = await helper.get_settings_data(chat, link.channel_id, message.from_user.id)

        await message.answer(text, reply_markup=markup, disable_web_page_preview=True)

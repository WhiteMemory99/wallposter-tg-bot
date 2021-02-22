from aiogram import types
from aiogram.dispatcher import FSMContext

from app.models import Channel, Link, Wallpaper
from app.utils import helper


async def show_settings_menu(query: types.CallbackQuery, state: FSMContext, link: Link):
    await state.finish()

    chat = await query.bot.get_chat(link.channel_id)
    text, markup = await helper.get_settings_data(chat, link.channel_id, query.from_user.id)

    await query.message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
    await query.answer()


async def show_status_menu(query: types.CallbackQuery, link: Link):
    chat = await query.bot.get_chat(link.channel_id)
    text, markup = await helper.get_status_data(chat, link.channel_id, query.from_user.id)

    await query.message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
    await query.answer()


async def show_queue_list(query: types.CallbackQuery, link: Link):
    images = (
        await Wallpaper.query.where(Wallpaper.user_id == query.from_user.id and Wallpaper.telegraph_link is not None)
        .limit(100)
        .gino.all()
    )

    if images:
        queue_list = []
        channel = await Channel.get(link.channel_id)
        current_counter = channel.counter_value
        for image in images:
            notification = " - следующие" if current_counter == channel.counter_value else ""
            queue_list.append(f'<a href="{image.telegraph_link}">Обои #{current_counter + 1}</a>{notification}')
            current_counter += 1

        links = "\n".join(queue_list)
        await query.message.edit_text(f"<b>Предпросмотр очереди:</b>\n\n{links}", disable_web_page_preview=True)
        await query.answer()
    else:
        await query.message.delete_reply_markup()
        await query.answer("Очередь публикации пустая.", show_alert=True)

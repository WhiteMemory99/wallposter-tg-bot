from aiogram import types

from app.models import User, Wallpaper


async def text_filler(call: types.CallbackQuery):
    await call.answer('Нажмите справа, чтобы переключить.', show_alert=True)


async def show_queue_list(call: types.CallbackQuery, user: User):
    images = await Wallpaper.query.where(
        Wallpaper.user_id == call.from_user.id and Wallpaper.telegraph_link is not None).gino.all()
    if images:
        text_list = []
        future_counter = user.counter
        for image in images[:100]:
            notification = ' - следующие' if future_counter == user.counter else ''
            text_list.append(f'<a href="{image.telegraph_link}">Обои #{future_counter + 1}</a>{notification}')
            future_counter += 1

        links = '\n'.join(text_list)
        await call.message.edit_text(f'<b>Предпросмотр очереди:</b>\n\n{links}', disable_web_page_preview=True)
        await call.answer()
    else:
        await call.message.delete_reply_markup()
        await call.answer('В данный момент нет доступных предпросмотров.', show_alert=True)

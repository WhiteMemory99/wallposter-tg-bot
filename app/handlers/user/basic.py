from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import BadRequest
from aiogram.utils.markdown import quote_html

from app.models import User, Wallpaper, db
from app.services import apscheduler
from app.utils import helper


async def greeting(message: types.Message):
    markup = InlineKeyboardMarkup().row(InlineKeyboardButton('Открыть настройки', callback_data='settings'))
    await message.answer(
        f'Привет, <b>{quote_html(message.from_user.first_name)}</b>!\n'
        f'Для подключения своего канала, добавь меня в него и перешли оттуда любое сообщение.',
        reply_markup=markup
    )


async def connect_channel(message: types.Message, user: User):
    try:
        administrators = await message.bot.get_chat_administrators(message.forward_from_chat.id)
        for member in administrators:
            if member.is_chat_creator() and member.user.id == message.from_user.id:
                chat_title = quote_html(message.forward_from_chat.title)
                if user.chat_id == message.forward_from_chat.id:
                    await message.answer(f'Канал <b>{chat_title}</b> уже подключён.')
                else:
                    status = 'изменён' if user.chat_id else 'подключён'
                    await user.update(chat_id=message.forward_from_chat.id, counter=0).apply()
                    await message.answer(
                        f'Канал <b>{chat_title}</b> {status}.\n'
                        'Теперь отправьте мне картинки документом, чтобы поставить их в очередь.'
                    )
                break
        else:
            await message.answer('Добавить канал можно только являясь его создателем.')
    except BadRequest:
        await message.answer('Сначала добавьте меня в этот канал.')


async def settings(message: types.Message, user: User):
    text, markup = helper.get_settings_data(user)
    await message.answer(text, reply_markup=markup)


async def show_status(message: types.Message, user: User):
    if user.chat_id:
        queue_size = await db.select([db.func.count()]).where(Wallpaper.user_id == message.from_user.id).gino.scalar()
        if queue_size > 0:
            markup = InlineKeyboardMarkup().add(
                InlineKeyboardButton('Обои в очереди', callback_data='queue_list')
            )
        else:
            markup = None

        job = apscheduler.get_job(f'posting_{message.from_user.id}')
        if job is not None:
            next_run = f'Следующая публикация:\n<b>{job.next_run_time.strftime("%d/%m, в %H:%M по %Z")}</b>'
        else:
            next_run = '<b>Планировщик остановлен...</b>'

        await message.answer(f'Обоев в очереди: <b>{queue_size}</b>\n\n{next_run}', reply_markup=markup)
    else:
        await message.answer('Для просмотра статуса <b>подключите свой канал с обоями</b>, переслав из него сообщение.')

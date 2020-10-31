from typing import Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models import User
from app.services.scheduler import apscheduler


POSITIVE = '✅'
NEGATIVE = '🔴'


def get_settings_data(user: User) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Get an inline keyboard object of the settings.

    :param user: User object from the database
    :return: Returns text and InlineKeyboardMarkup
    """
    job_id = f'posting_{user.id}'
    job = apscheduler.get_job(job_id)
    scheduler_status = POSITIVE if job is not None else NEGATIVE
    title_status = POSITIVE if user.enable_sign else NEGATIVE
    counter_status = POSITIVE if user.enable_counter else NEGATIVE

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton('Планировщик', callback_data='info'),
        InlineKeyboardButton(scheduler_status, callback_data='schedule_switch'),
        InlineKeyboardButton('Счётчик обоев', callback_data='info'),
        InlineKeyboardButton(counter_status, callback_data='counter_switch'),
        InlineKeyboardButton('Подпись', callback_data='info'),
        InlineKeyboardButton(title_status, callback_data='title_switch')
    )

    if job is not None:
        markup.row(InlineKeyboardButton('Редактировать интервал', callback_data='schedule_edit'))
    if user.enable_counter:
        markup.row(InlineKeyboardButton('Редактировать счётчик', callback_data='counter_edit'))
    if user.enable_sign:
        markup.row(InlineKeyboardButton('Редактировать подпись', callback_data='title_edit'))

    channel = user.chat_id if user.chat_id else 'Нет'
    interval_text = get_interval_text(user.scheduler_hours)
    text = f'<b>Настройки публикации.</b>\nКанал: <code>{channel}</code>\n' \
           f'Интервал планировщика: <b>{interval_text}</b>\nТекущий счётчик: <b>{user.counter}</b>'

    return text, markup


def get_interval_text(number: int) -> str:
    """
    Get the scheduler interval text based on its number.

    :param number: Scheduler interval hours
    :return:
    """
    if number in [1, 21]:
        text = f'{number} час'
    elif number in [2, 3, 4, 22, 23, 24]:
        text = f'{number} часа'
    else:
        text = f'{number} часов'

    return text

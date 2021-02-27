from typing import Tuple

from aiogram import md, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models import Channel, Wallpaper, db
from app.services.scheduler import BASE_JOB_ID, apscheduler

STATUS = {True: "✅", False: "🔴"}


async def get_settings_data(chat_obj: types.Chat, channel_id: int, user_id: int) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Get settings data for a wallpaper channel.

    :param chat_obj: Chat object to get its title from
    :param channel_id: ID of the connected channel
    :param user_id: User ID
    :return:
    """
    channel = await Channel.get(channel_id)

    markup = get_settings_markup(channel, user_id)
    channel_title = get_chat_title(chat_obj)
    interval_word = make_agree_with_number(channel.scheduler_hours, ("час", "часа", "часов"))

    text = (
        f"<b>{channel_title}</b>\nID: <code>{channel_id}</code>\nИнтервал планировщика: "
        f"<b>{channel.scheduler_hours} {interval_word}</b>\nТекущий счётчик: <b>{channel.counter_value}</b>"
    )

    return text, markup


def get_settings_markup(channel: Channel, user_id: int) -> InlineKeyboardMarkup:
    """
    Build the setting reply markup that can be accessed from anywhere.

    :param channel: Channel database object
    :param user_id: User ID
    :return:
    """
    job = apscheduler.get_job(BASE_JOB_ID.format(channel_id=channel.id, user_id=user_id))
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Планировщик", callback_data="switch_scheduler"),
        InlineKeyboardButton(STATUS[job is not None], callback_data="switch_scheduler"),
        InlineKeyboardButton("Счётчик обоев", callback_data="switch_counter"),
        InlineKeyboardButton(STATUS[channel.enable_counter], callback_data="switch_counter"),
        InlineKeyboardButton("Подпись", callback_data="switch_signature"),
        InlineKeyboardButton(STATUS[channel.enable_signature], callback_data="switch_signature"),
    )

    if job is not None:
        markup.row(InlineKeyboardButton("Редактировать интервал", callback_data="edit_scheduler"))
    if channel.enable_counter:
        markup.row(InlineKeyboardButton("Редактировать счётчик", callback_data="edit_counter"))
    if channel.enable_signature:
        markup.row(InlineKeyboardButton("Редактировать подпись", callback_data="edit_signature"))

    return markup


async def get_status_data(chat_obj: types.Chat, channel_id: int, user_id: int):
    """
    Get text and markup for functions that show the scheduler status.

    :param chat_obj: Chat object to get its title from
    :param channel_id: ID of the connected channel
    :param user_id: User ID
    :return:
    """
    queue_size = (
        await db.select([db.func.count()])
        .where(Wallpaper.user_id == user_id and Wallpaper.channel_id == channel_id)
        .gino.scalar()
    )
    if queue_size > 0:
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("Обои в очереди", callback_data="queue_list"))
    else:
        markup = None

    job = apscheduler.get_job(BASE_JOB_ID.format(channel_id=channel_id, user_id=user_id))
    if job is not None:
        next_run = f'<b>Следующая публикация:</b>\n<code>{job.next_run_time.strftime("%d/%m, в %H:%M по %Z")}</code>'
    else:
        next_run = "<b>Планировщик выключен...</b>"

    chat_title = get_chat_title(chat_obj)
    word = make_agree_with_number(queue_size, ("файл", "файла", "файлов"))
    text = f"Очередь <b>{chat_title}</b>:\n<code>{queue_size}</code> {word}\n\n{next_run}"

    return text, markup


def get_chat_title(chat: types.Chat) -> str:
    """
    Return a proper chat title with a text link when possible.

    :param chat: Chat object
    :return:
    """
    if chat.username:
        return f'<a href="https://t.me/{chat.username}">{chat.title}</a>'
    else:
        return md.quote_html(chat.title)


def make_agree_with_number(number: int, word_options: Tuple[str, str, str]) -> str:
    """
    Make a word agree with number. Used in places that need a proper word form with numbers.

    :param number: Number to make agree with
    :param word_options: Tuple with words: (1, 2/3/4, 5+/11-19)
    :return: Returns a proper word
    """
    num_suffix = number % 100
    if 11 <= num_suffix <= 19:  # An exception
        return word_options[2]
    else:
        num_suffix = num_suffix % 10
        if num_suffix == 1:
            return word_options[0]
        elif num_suffix in (2, 3, 4):
            return word_options[1]
        else:
            return word_options[2]

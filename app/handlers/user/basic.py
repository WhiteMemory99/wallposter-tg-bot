from aiogram import md, types
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import exceptions
from asyncpg.exceptions import UniqueViolationError

from app import config
from app.models import Channel, Link
from app.services.scheduler import BASE_JOB_ID, apscheduler
from app.utils import helper, keyboard, posting


async def greeting(message: types.Message):
    await message.answer(
        f"Привет, <b>{md.quote_html(message.from_user.first_name)}</b>!\n\n"
        "<b>1.</b> Для подключения канала добавь меня в него, затем перешли оттуда любое сообщение.\n"
        "<b>2.</b> После подключения канала просто отправь мне картинку в виде документа."
        " Я автоматически добавлю её в очередь публикации.\n"
        "<b>3.</b> Если захочешь сменить подключённый канал, просто перешли мне любое сообщение из нужного."
    )


async def get_sources_link(message: types.Message):
    me = await message.bot.me
    markup = InlineKeyboardMarkup().row(InlineKeyboardButton("GitHub", url=config.GITHUB_LINK))
    await message.answer(f"Исходный код <b>{me.first_name}</b> доступен по ссылке ниже.", reply_markup=markup)


async def handle_channel_forward(message: types.Message, link: Link):
    channel_title = md.quote_html(message.forward_from_chat.title)
    if link.channel_id == message.forward_from_chat.id:
        await message.answer(f"Канал <b>{channel_title}</b> уже подключён.")
        return

    try:
        member = await message.bot.get_chat_member(message.forward_from_chat.id, message.from_user.id)
        if member.is_chat_creator() or member.can_post_messages:
            try:
                channel = await Channel.create(id=message.forward_from_chat.id)
            except UniqueViolationError:
                channel = await Channel.get(message.forward_from_chat.id)

            await link.update(channel_id=message.forward_from_chat.id).apply()
            await message.answer(
                f"Канал <b>{channel_title}</b> подключён.\n"
                "Теперь отправьте мне картинки документом, чтобы поставить их в очередь.\n",
                reply_markup=keyboard.control_markup,
            )

            job_id = BASE_JOB_ID.format(channel_id=channel.id, user_id=message.from_user.id)
            job = apscheduler.get_job(job_id)
            if job is None:
                apscheduler.add_job(
                    posting.post_wallpaper,
                    id=job_id,
                    trigger="cron",
                    minute="0",
                    hour=f"*/{channel.scheduler_hours}",
                    args=(channel.id, message.from_user.id),
                    replace_existing=True,
                )
        else:
            await message.answer(
                "Для добавления канала необходимо быть его администратором с правом публикации сообщений."
            )
    except exceptions.Unauthorized:
        await message.answer(f"Сначала добавьте меня в <b>{channel_title}</b>.")


async def settings_command(message: types.Message, link: Link):
    if link.channel_id:
        chat = await message.bot.get_chat(link.channel_id)
        text, markup = await helper.get_settings_data(chat, link.channel_id, message.from_user.id)

        await message.answer(text, reply_markup=markup, disable_web_page_preview=True)
    else:
        await message.answer("Для входа в настройки сначала подключите канал с обоями.")


async def status_command(message: types.Message, link: Link):
    if link.channel_id:
        chat = await message.bot.get_chat(link.channel_id)
        text, markup = await helper.get_status_data(chat, link.channel_id, message.from_user.id)

        await message.answer(text, reply_markup=markup, disable_web_page_preview=True)
    else:
        await message.answer("Для просмотра статуса сначала подключите канал с обоями.")

from dataclasses import dataclass
from io import BytesIO
from typing import Tuple

from aiogram import Bot, md
from aiogram.types import InputFile
from aiogram.utils import exceptions
from loguru import logger
from PIL import Image
from sqlalchemy.sql import and_

from app.models import Channel, Wallpaper, db
from app.services.scheduler import BASE_JOB_ID, apscheduler
from app.utils import helper, keyboard


@dataclass
class PostingData:
    wallpaper_id: int
    user_id: int
    channel_id: int
    file_id: str
    extension: str
    custom_signature: str
    enable_signature: bool
    signature_text: str
    enable_counter: bool
    counter_value: int


async def post_wallpaper(channel_id: int, user_id: int) -> None:
    """
    This function is used by the apscheduler to post wallpapers.

    :param channel_id: Channel ID to publish wallpaper in
    :param user_id: User ID
    :return:
    """
    queue_element = (
        await db.select(
            [
                Wallpaper.id,
                Wallpaper.user_id,
                Wallpaper.channel_id,
                Wallpaper.file_id,
                Wallpaper.extension,
                Wallpaper.custom_signature,
                Channel.enable_signature,
                Channel.signature_text,
                Channel.enable_counter,
                Channel.counter_value,
            ]
        )
        .select_from(Wallpaper.join(Channel))
        .where(and_(Wallpaper.channel_id == channel_id, Wallpaper.user_id == user_id))
        .gino.first()
    )
    if queue_element is None:
        return

    bot = Bot.get_current()
    job = apscheduler.get_job(BASE_JOB_ID.format(channel_id=channel_id, user_id=user_id))
    data = PostingData(*queue_element)

    filename, caption, chat_title = await gather_file_data(bot, data)
    member = await bot.get_chat_member(channel_id, user_id)
    if not member.is_chat_creator() and not member.can_post_messages:
        try:
            await bot.send_message(
                user_id, f"Вы потеряли админку в <b>{chat_title}</b>.\nВсе публикации в этот канал отменены."
            )
        finally:
            await Wallpaper.delete.where(
                and_(Wallpaper.user_id == data.user_id, Wallpaper.channel_id == data.channel_id)
            ).gino.status()
            if job is not None:
                job.remove()

    try:
        with await bot.download_file_by_id(data.file_id) as full_image:
            with resize_image(full_image) as preview_image:
                await bot.send_photo(channel_id, InputFile(preview_image), caption=caption)
                await bot.send_document(
                    channel_id, InputFile(full_image, filename=filename), disable_notification=True
                )

                await Channel.update.values(counter_value=data.counter_value + 1).gino.status()
                await Wallpaper.delete.where(Wallpaper.id == data.wallpaper_id).gino.status()
    except exceptions.TelegramAPIError as ex:
        logger.error("{ex} while publishing a wallpaper.", ex=ex)
        try:
            await bot.send_message(
                user_id,
                f"Произошла ошибка при публикации в <b>{chat_title}</b>!\n"
                "Проверьте канал и права бота, затем перезапустите планировщик.",
                reply_markup=keyboard.control_markup,
                disable_web_page_preview=True,
            )
        finally:
            if job is not None:
                job.remove()


async def gather_file_data(bot: Bot, data: PostingData) -> Tuple[str, str, str]:
    """
    Build and return output filename and caption for further processing.

    :param channel: Channel database object
    :param file: Wallpaper database object
    :return: Filename, caption and chat title
    """
    chat = await bot.get_chat(data.channel_id)
    if data.extension == "jpeg" or data.extension is None:
        extension = "jpg"
    else:
        extension = data.extension

    base_name = chat.username or chat.title.replace(" ", "_")
    if data.enable_counter:
        filename = f"{base_name.lower()}-{data.counter_value + 1}.{extension}"
    else:
        filename = f"{base_name.lower()}.{extension}"

    if chat.username:
        title_signature = f'<a href="https://t.me/{chat.username}">{chat.username}</a>'
    else:
        title_signature = md.quote_html(chat.title)

    if data.custom_signature:
        caption = data.custom_signature.replace("{title}", title_signature)
    elif data.enable_signature:
        if data.signature_text:
            caption = data.signature_text.replace("{title}", title_signature)
        else:
            caption = title_signature
    else:
        caption = None

    return filename, caption, helper.get_chat_title(chat)


def resize_image(image: BytesIO) -> BytesIO:
    """
    Telegram has some restrictions, so we resize image into HD previews to avoid errors.

    :param file_path: Path to an image
    :return: Returns a new path
    """
    img = Image.open(image)
    img.thumbnail((1280, 1280), Image.ANTIALIAS)

    preview_image = BytesIO()
    img.save(preview_image, "PNG")

    image.seek(0)
    preview_image.seek(0)

    return preview_image

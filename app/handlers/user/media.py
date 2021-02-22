from io import BytesIO
from typing import Optional

import httpx
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from gino.exceptions import NoSuchRowError

from app.models import Link, Wallpaper
from app.utils import helper
from app.utils.callback_data import wallpaper_cd


async def photo_receiver(message: types.Message, link: Link):
    if not link.channel_id:
        await message.answer("Для публикации обоев сначала подключите канал.")
        return

    if "image" in message.document.mime_type:
        if message.document.file_size > 20000000:  # TODO: Local Bot API / Pyrogram
            await message.answer("Размер этой картинки слишком большой для публикации через меня.")
            return

        image = await Wallpaper.query.where(
            Wallpaper.unique_file_id == message.document.file_unique_id and Wallpaper.channel_id == link.channel_id
        ).gino.first()

        chat = await message.bot.get_chat(link.channel_id)
        chat_title = helper.get_chat_title(chat)
        if image is None:
            if message.caption and not message.is_forward():
                custom_signature = message.html_text
            else:
                custom_signature = None

            image = await Wallpaper.create(
                file_id=message.document.file_id,
                unique_file_id=message.document.file_unique_id,
                user_id=message.from_user.id,
                channel_id=link.channel_id,
                extension=message.document.mime_type.split("/")[1],
                custom_signature=custom_signature,
            )

            caption_text = f"\n\n<b>Кастомная подпись:</b>\n{custom_signature}" if custom_signature else ""
            await message.reply(
                f"Файл добавлен в очередь на публикацию в <b>{chat_title}</b>.{caption_text}",
                reply_markup=get_publishing_keyboard(image.id, link.channel_id),
                disable_web_page_preview=True,
            )

            telegraph_link = await upload_telegraph_preview(message.document)
            try:
                await image.update(telegraph_link=telegraph_link).apply()
            except NoSuchRowError:
                return
        else:
            await message.reply(
                f"Эта картинка уже в очереди на публикацию в <b>{chat_title}</b>.",
                reply_markup=get_publishing_keyboard(image.id, link.channel_id),
                disable_web_page_preview=True,
            )
    else:
        await message.reply("Я принимаю только документы с картинками.")


def get_publishing_keyboard(wallpaper_id: int, channel_id: int) -> InlineKeyboardMarkup:
    """
    Get a keyboard containing publishing options.

    :param wallpaper_id: Database ID of a wallpaper
    :return:
    """
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            "Опубликовать сейчас",
            callback_data=wallpaper_cd.new(wall_id=wallpaper_id, chat_id=channel_id, do="publish"),
        ),
        InlineKeyboardButton(
            "Снять с очереди", callback_data=wallpaper_cd.new(wall_id=wallpaper_id, chat_id=channel_id, do="discard")
        ),
    )


async def upload_telegraph_preview(document: types.Document) -> Optional[str]:
    """
    Upload a wallpaper to Telegraph. This preview will be used in the queue list.

    :param document: Original document object
    :param user_id: User ID
    :return: Returns a telegraph link on success
    """
    with await document.download(destination=BytesIO()) as image:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://telegra.ph/upload",
                    files={"upload-file": ("wallpaper_preview", image, "image/png")},
                )
                result = response.json()
                if "error" in result:
                    return None

                return f'https://telegra.ph{result[0]["src"]}'
            except httpx.HTTPError:
                return None

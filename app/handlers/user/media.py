import os
import tempfile
from typing import Optional

import httpx
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models import User, Wallpaper
from app.utils.posting import resize_image


async def photo_receiver(message: types.Message, user: User):
    if user.chat_id:
        if 'image' in message.document.mime_type:
            image = await Wallpaper.query.where(Wallpaper.unique_id == message.document.file_unique_id).gino.first()
            if image is None:
                if message.caption and len(message.caption) <= 100:
                    sign_text = message.html_text
                else:
                    sign_text = None

                image = await Wallpaper.create(
                    file_id=message.document.file_id,
                    unique_id=message.document.file_unique_id,
                    user_id=message.from_user.id,
                    extension=message.document.mime_type.split('/')[1],
                    custom_sign=sign_text,
                )
                caption_text = f'\n\n<b>Кастомная подпись:</b>\n{sign_text}' if sign_text else ''
                await message.reply(
                    f'Картинка добавлена в очередь на публикацию.{caption_text}',
                    reply_markup=get_control_keyboard(image.id)
                )

                # It takes some time so we upload a preview after the message was sent
                telegraph_link = await upload_preview(message.document, message.from_user.id)
                try:
                    await image.update(telegraph_link=telegraph_link).apply()
                except Exception:
                    return
            else:
                await message.reply(
                    'Эта картинка уже в очереди на публикацию.',
                    reply_markup=get_control_keyboard(image.id)
                )
        else:
            await message.reply('Я принимаю только картинки и фотографии.')
    else:
        await message.answer('Сначала добавьте свой канал, переслав из него сообщение.')


def get_control_keyboard(wallpaper_id: int) -> InlineKeyboardMarkup:
    """
    Get a keyboard containing publishing options.

    :param wallpaper_id: Database ID of the wallpaper
    :return:
    """
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton('Опубликовать сейчас', callback_data=f'publish_{wallpaper_id}'),
        InlineKeyboardButton('Снять с очереди', callback_data=f'remove_{wallpaper_id}')
    )


async def upload_preview(document: types.Document, user_id: int) -> Optional[str]:
    """
    Upload a wallpaper to Telegraph. This preview will be used in the queue list.

    :param document: Original document object
    :param user_id: User ID
    :return: Returns a telegraph link on success
    """
    with tempfile.TemporaryDirectory(prefix=str(user_id), suffix='upload') as tempdir:
        full_path = await document.download(destination=os.path.join(tempdir, document.file_id))
        preview_path = resize_image(full_path.name)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    'https://telegra.ph/upload',
                    files={'upload-file': ('wallpaper_preview', open(preview_path, 'rb'), 'image/jpeg')}
                )
                result = response.json()
                if 'error' in result:
                    return None

                return f'https://telegra.ph{result[0]["src"]}'
            except httpx.HTTPError:
                return None

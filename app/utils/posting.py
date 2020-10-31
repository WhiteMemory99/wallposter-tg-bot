import os
import tempfile
from typing import Tuple

from PIL import Image
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from aiogram.utils.exceptions import TelegramAPIError
from aiogram.utils.markdown import quote_html

from app.misc import bot
from app.models import User, Wallpaper
from app.services import apscheduler


async def post_wallpaper(user_id: int) -> None:
    """
    This function is used by the apscheduler to post a wallpaper.

    :param user_id: ID of a channel owner
    :return:
    """
    image = await Wallpaper.query.where(Wallpaper.user_id == user_id).gino.first()
    if image is not None:
        user = await User.get(user_id)
        if user.chat_id:
            filename, caption = await build_file_data(user, image)
            try:
                with tempfile.TemporaryDirectory(prefix=str(user_id)) as tempdir:
                    full_path = await bot.download_file_by_id(
                        image.file_id,
                        destination=os.path.join(tempdir, image.file_id)
                    )
                    preview_path = resize_image(full_path.name)
                    await bot.send_photo(user.chat_id, InputFile(preview_path), caption=caption)
                    await bot.send_document(
                        user.chat_id,
                        InputFile(full_path.name, filename=filename),
                        disable_notification=True
                    )

                await user.update(counter=user.counter + 1).apply()
                await image.delete()
            except TelegramAPIError:
                markup = InlineKeyboardMarkup().row(InlineKeyboardButton('Открыть настройки', callback_data='settings'))
                try:
                    await bot.send_message(
                        user_id,
                        'Произошла ошибка при публикации!\nПроверьте канал и права бота, затем запустите планировщик.',
                        reply_markup=markup
                    )
                finally:
                    job = apscheduler.get_job(f'posting_{user_id}')
                    if job is not None:
                        job.remove()


async def build_file_data(user: User, image: Wallpaper) -> Tuple[str, str]:
    """
    Build and return output filename and its caption for the further processing.

    :param user: User database object
    :param image: Wallpaper database object
    :return: Filename and caption
    """
    chat = await bot.get_chat(user.chat_id)
    base_name = chat.username or chat.title.replace(' ', '_')
    if image.extension == 'jpeg' or image.extension is None:
        extension = 'jpg'
    else:
        extension = image.extension

    if user.enable_counter:
        filename = f'{base_name.lower()}-{user.counter + 1}.{extension}'
    else:
        filename = f'{base_name.lower()}.{extension}'

    if user.enable_sign:
        link = await chat.get_url()
        if link:
            chat_sign = f'<a href="{link}">{chat.username or chat.title}</a>'
        else:
            chat_sign = quote_html(chat.title)

        if image.custom_sign:
            caption = image.custom_sign.replace('{sign}', chat_sign)
        else:
            if user.sign_text:
                caption = user.sign_text.replace('{sign}', chat_sign)
            else:
                caption = chat_sign
    else:
        caption = None

    return filename, caption


def resize_image(path: str) -> str:
    """
    Telegram has some restrictions, so we resize photos into HD previews to avoid errors.

    :param path: Original path to the photo
    :return: Returns a new path
    """
    new_path = f'{path}_preview'

    img = Image.open(path)
    img.thumbnail((1280, 1280), Image.ANTIALIAS)
    img.save(new_path, 'JPEG')

    return new_path

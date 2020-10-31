import os
import tempfile

from aiogram import types
from aiogram.types import InputFile
from aiogram.utils.exceptions import TelegramAPIError

from app.models import User, Wallpaper
from app.services import apscheduler
from app.utils.posting import build_file_data, resize_image


async def cancel_publishing(call: types.CallbackQuery):
    wallpaper_id = int(call.data.split('_')[1])
    await call.message.delete_reply_markup()

    image = await Wallpaper.get(wallpaper_id)
    if image is not None:
        await image.delete()
        await call.answer('Файл снят с очереди.')
    else:
        await call.answer('Этот файл уже был опубликован или снят с очереди.', show_alert=True)


async def publish_now(call: types.CallbackQuery, user: User):
    wallpaper_id = int(call.data.split('_')[1])
    await call.message.delete_reply_markup()

    image = await Wallpaper.get(wallpaper_id)
    if image is not None:
        if user.chat_id:
            filename, caption = await build_file_data(user, image)
            try:
                with tempfile.TemporaryDirectory(prefix=str(user.id)) as tempdir:
                    full_path = await call.bot.download_file_by_id(
                        image.file_id,
                        destination=os.path.join(tempdir, image.file_id)
                    )
                    preview_path = resize_image(full_path.name)
                    await call.bot.send_photo(user.chat_id, InputFile(preview_path), caption=caption)
                    await call.bot.send_document(
                        user.chat_id,
                        InputFile(full_path.name, filename=filename),
                        disable_notification=True
                    )

                await user.update(counter=user.counter + 1).apply()
                await image.delete()
                await call.answer('Файл успешно опубликован.')
            except TelegramAPIError:
                job = apscheduler.get_job(f'posting_{user.id}')
                if job is not None:
                    job.remove()

                await call.answer(
                    'Произошла ошибка при отправке.\nПроверьте канал и права бота, затем снова запустите планировщик.',
                    show_alert=True
                )
    else:
        await call.answer('Этот файл уже был опубликован или снят с очереди.', show_alert=True)

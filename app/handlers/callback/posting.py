from aiogram import types
from aiogram.types import InputFile
from aiogram.utils import exceptions
from loguru import logger

from app.models import Channel, Wallpaper, db
from app.services.scheduler import BASE_JOB_ID, apscheduler
from app.utils.posting import PostingData, gather_file_data, resize_image


async def cancel_publishing(query: types.CallbackQuery, callback_data: dict):
    wallpaper_id = int(callback_data["wall_id"])
    await query.message.delete_reply_markup()

    image = await Wallpaper.get(wallpaper_id)
    if image is not None:
        await image.delete()
        await query.answer("Файл снят с очереди.")
    else:
        await query.answer("Этот файл уже был опубликован или снят с очереди.", show_alert=True)


async def publish_now(query: types.CallbackQuery, callback_data: dict):
    wallpaper_id = int(callback_data["wall_id"])
    channel_id = int(callback_data["chat_id"])
    await query.message.delete_reply_markup()

    image = (
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
        .where(Wallpaper.channel_id == channel_id and Wallpaper.id == wallpaper_id)
        .gino.first()
    )
    if image is not None:
        job = apscheduler.get_job(BASE_JOB_ID.format(channel_id=image.channel_id, user_id=query.from_user.id))
        member = await query.bot.get_chat_member(channel_id, query.from_user.id)
        if not member.is_chat_creator() and not member.can_post_messages:
            try:
                await query.answer("Вы потеряли админку в канале.\nВсе публикации отменены.")
            finally:
                await Wallpaper.delete.where(
                    Wallpaper.user_id == query.from_user.id and Wallpaper.channel_id == channel_id
                ).gino.status()
                if job is not None:
                    job.remove()

        data = PostingData(*image)
        filename, caption, _ = await gather_file_data(query.bot, data)
        try:
            with await query.bot.download_file_by_id(image.file_id) as full_image:
                with resize_image(full_image) as preview_image:
                    await query.bot.send_photo(image.channel_id, InputFile(preview_image), caption=caption)
                    await query.bot.send_document(
                        image.channel_id, InputFile(full_image, filename=filename), disable_notification=True
                    )

                    await Channel.update.values(counter_value=data.counter_value + 1).gino.status()
                    await Wallpaper.delete.where(Wallpaper.id == wallpaper_id).gino.status()

            await query.answer("Файл успешно опубликован.")
        except exceptions.TelegramAPIError as ex:
            logger.error("{ex} while publishing a wallpaper.", ex=ex)
            if job is not None:
                job.remove()

            await query.answer(
                "Произошла ошибка при публикации.\nПроверьте канал и права бота, затем перезапустите планировщик.",
                show_alert=True,
            )
    else:
        await query.answer("Этот файл уже был опубликован или снят с очереди.", show_alert=True)

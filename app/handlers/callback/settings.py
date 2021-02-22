from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models import Channel, Link
from app.services.scheduler import BASE_JOB_ID, apscheduler
from app.utils import helper, posting
from app.utils.callback_data import interval_cd
from app.utils.states import Inputs


async def settings_switchers(query: types.CallbackQuery, link: Link):  # TODO: Validate Channel ID is equal
    channel = await Channel.get(link.channel_id)
    if query.data == "switch_counter":
        await channel.update(enable_counter=not channel.enable_counter).apply()
    elif query.data == "switch_signature":
        await channel.update(enable_signature=not channel.enable_signature).apply()
    else:
        job_id = BASE_JOB_ID.format(channel_id=channel.id, user_id=query.from_user.id)
        job = apscheduler.get_job(job_id)
        if job is None:
            apscheduler.add_job(
                posting.post_wallpaper,
                id=job_id,
                trigger="cron",
                minute="0",
                hour=f"*/{channel.scheduler_hours}",
                args=(channel.id, query.from_user.id),
                replace_existing=True,
            )
        else:
            job.remove()

    markup = helper.get_settings_markup(channel, query.from_user.id)
    await query.message.edit_reply_markup(markup)
    await query.answer()


async def edit_settings_values(query: types.CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=2)
    if query.data == "edit_signature":
        markup.add(
            InlineKeyboardButton("По-умолчанию", callback_data="reset_signature"),
            InlineKeyboardButton("Отмена", callback_data="open_settings"),
        )
        await query.message.edit_text(
            "Отправьте новую подпись, она будет под каждой публикацией."
            "\n<code>{title}</code> - Актуальное название канала в ссылке, оно же стоит по-умолчанию.",
            reply_markup=markup,
        )

        await Inputs.edit_signature.set()
    elif query.data == "edit_counter":
        markup.add(InlineKeyboardButton("Отмена", callback_data="open_settings"))
        await query.message.edit_text(
            "Отправьте значение счётчика от <b>0</b> до <b>100000000</b>.\n"
            "Он служит основой для нумерации файлов в названии.",
            reply_markup=markup,
        )

        await Inputs.edit_counter.set()
    else:
        for interval in range(0, 25, 3):
            if not interval:
                interval += 1

            word = helper.make_agree_with_number(interval, ("час", "часа", "часов"))
            markup.insert(
                InlineKeyboardButton(f"Раз в {interval} {word}", callback_data=interval_cd.new(hours=interval))
            )

        await query.message.edit_reply_markup(markup)

    await query.answer()


async def reset_signature(query: types.CallbackQuery, state: FSMContext, link: Link):
    await state.finish()
    await Channel.update.values(signature_text=None).where(Channel.id == link.channel_id).gino.status()

    chat = await query.bot.get_chat(link.channel_id)
    text, markup = await helper.get_settings_data(chat, link.channel_id, query.from_user.id)
    await query.message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)

    await query.answer("Подпись сброшена к стандартному значению.")


async def edit_scheduler_interval(query: types.CallbackQuery, callback_data: dict, link: Link):
    hours = int(callback_data["hours"])
    await Channel.update.values(scheduler_hours=hours).where(Channel.id == link.channel_id).gino.status()

    job = apscheduler.get_job(BASE_JOB_ID.format(channel_id=link.channel_id, user_id=query.from_user.id))
    if job is not None:
        job.reschedule(trigger="cron", minute="0", hour=f"*/{hours}")

    chat = await query.bot.get_chat(link.channel_id)
    text, markup = await helper.get_settings_data(chat, link.channel_id, query.from_user.id)
    await query.message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
    await query.answer()

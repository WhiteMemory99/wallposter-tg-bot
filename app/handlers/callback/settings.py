from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models import User
from app.services import apscheduler
from app.utils import helper, posting
from app.utils.states import Inputs


async def settings_switchers(call: types.CallbackQuery, user: User):
    if call.data == 'counter_switch':
        await user.update(enable_counter=not user.enable_counter).apply()
    elif call.data == 'title_switch':
        await user.update(enable_sign=not user.enable_sign).apply()
    else:
        job_id = f'posting_{call.from_user.id}'
        job = apscheduler.get_job(job_id)
        if job is None:
            apscheduler.add_job(
                posting.post_wallpaper,
                id=job_id,
                trigger='cron',
                minute='0',
                hour=f'*/{user.scheduler_hours}',
                args=(call.from_user.id,),
                replace_existing=True
            )
        else:
            job.remove()

    _, markup = helper.get_settings_data(user)
    await call.message.edit_reply_markup(markup)
    await call.answer()


async def edit_settings_options(call: types.CallbackQuery, state: FSMContext):
    markup = InlineKeyboardMarkup(row_width=1)
    if call.data == 'title_edit':
        markup.add(
            InlineKeyboardButton('По-умолчанию', callback_data='title_reset'),
            InlineKeyboardButton('Назад', callback_data='settings')
        )
        await call.message.edit_text(
            'Введите новый текст, который будет под каждой публикацией.'
            '\n<code>{sign}</code> - Актуальная подпись с именем канала.',
            reply_markup=markup
        )

        await Inputs.edit_sign.set()
        await state.update_data(message_id=call.message.message_id)
    elif call.data == 'counter_edit':
        markup.add(InlineKeyboardButton('Назад', callback_data='settings'))
        await call.message.edit_text(
            'Введите отправное значение счётчика <b>от 0 до 1000000</b>.\nОн отвечает за нумерацию файлов в названии.',
            reply_markup=markup
        )

        await Inputs.edit_counter.set()
        await state.update_data(message_id=call.message.message_id)
    else:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton('Раз в 1 час', callback_data='interval_1'),
            InlineKeyboardButton('Раз в 3 часа', callback_data='interval_3'),
            InlineKeyboardButton('Раз в 6 часов', callback_data='interval_6'),
            InlineKeyboardButton('Раз в 9 часов', callback_data='interval_9'),
            InlineKeyboardButton('Раз в 12 часов', callback_data='interval_12')
        )
        await call.message.edit_reply_markup(markup)

    await call.answer()


async def reset_sign(call: types.CallbackQuery, user: User, state: FSMContext):
    await state.reset_state()
    await user.update(sign_text=None).apply()

    text, markup = helper.get_settings_data(user)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer('Подпись сброшена.')


async def edit_scheduler_interval(call: types.CallbackQuery, user: User):
    hours = int(call.data.split('_')[1])
    await user.update(scheduler_hours=hours).apply()
    job = apscheduler.get_job(f'posting_{call.from_user.id}')
    if job is not None:
        job.reschedule(
            trigger='cron',
            minute='0',
            hour=f'*/{hours}'
        )

    text, markup = helper.get_settings_data(user)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


async def show_settings_menu(call: types.CallbackQuery, user: User, state: FSMContext):
    await state.reset_state()

    text, markup = helper.get_settings_data(user)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()

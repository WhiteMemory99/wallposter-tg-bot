from aiogram import Dispatcher

from app.handlers.callback import common, posting, settings


def setup(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(
        common.text_filler,
        text='info',
        state='*'
    )

    dispatcher.register_callback_query_handler(
        common.show_queue_list,
        text='queue_list',
        state='*'
    )

    dispatcher.register_callback_query_handler(
        posting.publish_now,
        text_startswith='publish_',
        state='*'
    )

    dispatcher.register_callback_query_handler(
        posting.cancel_publishing,
        text_startswith='remove_',
        state='*'
    )

    dispatcher.register_callback_query_handler(
        settings.show_settings_menu,
        text='settings',
        state='*'
    )

    dispatcher.register_callback_query_handler(
        settings.reset_sign,
        text='title_reset',
        state='*'
    )

    dispatcher.register_callback_query_handler(
        settings.edit_scheduler_interval,
        text_startswith='interval_',
        state='*'
    )

    dispatcher.register_callback_query_handler(
        settings.settings_switchers,
        text=['title_switch', 'counter_switch', 'schedule_switch'],
        state='*'
    )

    dispatcher.register_callback_query_handler(
        settings.edit_settings_options,
        text=['schedule_edit', 'title_edit', 'counter_edit'],
        state='*'
    )

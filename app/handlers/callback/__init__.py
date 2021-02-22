from aiogram import Dispatcher

from app.handlers.callback import common, posting, settings
from app.utils.callback_data import interval_cd, wallpaper_cd


def setup(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(common.show_queue_list, text="queue_list", state="*")

    dispatcher.register_callback_query_handler(common.show_settings_menu, text="open_settings", state="*")

    dispatcher.register_callback_query_handler(common.show_status_menu, text="open_status", state="*")

    dispatcher.register_callback_query_handler(posting.publish_now, wallpaper_cd.filter(do="publish"), state="*")

    dispatcher.register_callback_query_handler(posting.cancel_publishing, wallpaper_cd.filter(do="discard"), state="*")

    dispatcher.register_callback_query_handler(settings.reset_signature, text="reset_signature", state="*")

    dispatcher.register_callback_query_handler(settings.edit_scheduler_interval, interval_cd.filter(), state="*")

    dispatcher.register_callback_query_handler(
        settings.settings_switchers, text=("switch_signature", "switch_counter", "switch_scheduler"), state="*"
    )

    dispatcher.register_callback_query_handler(
        settings.edit_settings_values, text=("edit_scheduler", "edit_signature", "edit_counter"), state="*"
    )

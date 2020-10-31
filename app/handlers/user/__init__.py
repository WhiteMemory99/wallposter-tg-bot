from aiogram import Dispatcher
from aiogram.types import ContentType

from app.handlers.user import basic, input, media
from app.utils.states import Inputs


def setup(dispatcher: Dispatcher):
    dispatcher.register_message_handler(
        input.new_title,
        state=Inputs.edit_sign,
        content_types=ContentType.ANY
    )

    dispatcher.register_message_handler(
        input.new_counter,
        state=Inputs.edit_counter,
        content_types=ContentType.ANY
    )

    dispatcher.register_message_handler(
        basic.greeting,
        commands=['start', 'help']
    )

    dispatcher.register_message_handler(
        basic.show_status,
        commands='status'
    )

    dispatcher.register_message_handler(
        basic.settings,
        commands='settings'
    )

    dispatcher.register_message_handler(
        basic.connect_channel,
        lambda msg: msg.forward_from_chat and msg.forward_from_chat.type == 'channel',
        content_types=ContentType.ANY
    )

    dispatcher.register_message_handler(
        media.photo_receiver,
        content_types=ContentType.DOCUMENT
    )

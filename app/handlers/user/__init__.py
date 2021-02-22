from aiogram import Dispatcher
from aiogram.types import ContentType

from app.handlers.user import basic, input, media
from app.utils.states import Inputs


def setup(dispatcher: Dispatcher):
    dispatcher.register_message_handler(media.photo_receiver, content_types=ContentType.DOCUMENT)

    dispatcher.register_message_handler(
        input.edit_signature, state=Inputs.edit_signature, content_types=ContentType.ANY
    )

    dispatcher.register_message_handler(
        input.edit_counter_value, state=Inputs.edit_counter, content_types=ContentType.ANY
    )

    dispatcher.register_message_handler(basic.greeting, commands=("start", "help"))

    dispatcher.register_message_handler(basic.status_command, commands="status")

    dispatcher.register_message_handler(basic.settings_command, commands="settings")

    dispatcher.register_message_handler(
        basic.handle_channel_forward,
        lambda msg: msg.forward_from_chat and msg.forward_from_chat.type == "channel",
        content_types=ContentType.ANY,
    )

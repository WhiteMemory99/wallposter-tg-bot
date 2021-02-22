from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

control_markup = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Настройки публикации", callback_data="open_settings"),
    InlineKeyboardButton("Статус планировщика", callback_data="open_status"),
)

from aiogram.dispatcher.filters.state import State, StatesGroup


class Inputs(StatesGroup):
    edit_signature = State()
    edit_counter = State()

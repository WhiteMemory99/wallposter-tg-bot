from aiogram.dispatcher.filters.state import State, StatesGroup


class Inputs(StatesGroup):
    edit_sign = State()
    edit_counter = State()

from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    choice_language = State()
    add_word = State()
    add_image = State()

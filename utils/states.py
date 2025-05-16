from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    choice_language = State()
    add_word = State()
    add_image = State()
    delete_word = State()
    clear_dict = State()
    guess_translation = State()
    show_cards = State()
    write_translation = State()
    write_original = State()
    choice_translation = State()
    end = State()


class WordToCardGame(StatesGroup):
    in_game = State()
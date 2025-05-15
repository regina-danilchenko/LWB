from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from datetime import datetime

from data import db_session
from data.user import User
from data.word import Word
from data.image import Image

from utils.functions import translate

from utils.common import print_text
from utils.states import Form


# Создаём роутер
add_router = Router()


# команда добавления нового слова
@add_router.message(Command('add'))
@add_router.callback_query(lambda c: c.data == "add")
async def process_add(request: Message, state: FSMContext):
    await state.set_state(Form.add_word)
    text = 'Введите слово, которое хотите выучить.'
    await print_text(request, text)


# добавление слова
@add_router.message(Form.add_word)
async def add_word(message: Message, state: FSMContext):
    await state.set_state(Form.add_image)
    original_word = message.text
    db_sess = db_session.create_session()
    language = db_sess.query(User).filter(User.tg_id == message.from_user.id).first().language_preference

    # перевод слова
    translated_word = translate(original_word.capitalize(), language)

    # добавление в словарь слова
    db_sess = db_session.create_session()
    word = Word()
    word.original_word = translated_word.capitalize()
    word.translation = original_word.capitalize()
    word.last_reviewed = datetime.now()
    db_sess.add(word)
    db_sess.commit()

    # добавление в словарь и добавление связи в таблицу связей user_to_word двух таблиц user и word
    db_sess = db_session.create_session()
    user_id = message.from_user.id
    user = db_sess.query(User).filter(User.tg_id == user_id).first()
    user.words.append(word)
    id_word = word.id
    db_sess.commit()

    # передача id слова в следующую функцию
    await state.update_data(id_word=id_word)
    await message.answer('Добавьте изображение к слову, чтобы лучше его запомнить.')


# добавление изображения и вывод результата
@add_router.message(Form.add_image)
async def add_image(message: Message, state: FSMContext):
    try:
        photos = message.photo
        file_id = photos[-1].file_id

        # получение id из прошлой функции
        data = await state.get_data()
        await state.clear()
        db_sess = db_session.create_session()
        word = db_sess.query(Word).filter(Word.id == data["id_word"]).first()

        # добавление изображения
        db_sess = db_session.create_session()
        image = Image()
        image.word_id = word.id
        image.file_id = file_id
        db_sess.add(image)
        db_sess.commit()

        text = (f'Вы добавили в словарь новое слово!\n'
                             f'\n'
                             f'Слово: {word.original_word.capitalize()}\n'
                             f'Перевод: {word.translation.capitalize()}\n'
                             f'Дата добавленя: {datetime.now().strftime("%d.%m.%Y")}\n'
                             f'\n'
                             f'👍Так держать!👍')

        await message.answer_photo(photo=file_id, caption=text)
    except TypeError:
        await message.answer('Неподдерживаемый формат для изображений. Выберите изображение.')

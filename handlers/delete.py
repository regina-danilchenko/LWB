from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup

from data import db_session
from data.user import User
from data.word import Word
from data.image import Image

from utils.common import print_text
from utils.states import Form


# Создаём роутер
delete_router = Router()


# получение слова, которое пользователь хочет удалить
@delete_router.message(Command('delete'))
@delete_router.callback_query(lambda c: c.data == "delete")
async def get_word_for_delete(request: Message | CallbackQuery, state: FSMContext):
    db_sess = db_session.create_session()
    user_id = request.from_user.id
    words = [user.words for user in db_sess.query(User).filter(User.tg_id == user_id).all()][0]
    if not words:
        text = '⚠️ Ваш словарь пуст! Вам нечего удалять!'
        await print_text(request, text)
    else:
        await state.set_state(Form.delete_word)
        text = '⌨️ Введите слово, которое хотите удалить.'
        await print_text(request, text)


# удаление этого слова
@delete_router.message(Form.delete_word)
async def delete_word(request: Message, state: FSMContext):
    word_to_delete = request.text.capitalize()
    db_sess = db_session.create_session()
    user_id = request.from_user.id
    words = [user.words for user in db_sess.query(User).filter(User.tg_id == user_id).all()][0]

    new_words = list()
    for word in words:
        new_words.append(word.original_word.capitalize())
        new_words.append(word.translation.capitalize())

    if word_to_delete not in new_words:
        text = '⚠️ В вашем словаре такого слова нет. Проверьте, не опечатались ли вы.'
        await print_text(request, text)
        await state.clear()
    else:
        word = db_sess.query(Word).filter(
            (Word.original_word == word_to_delete) |
            (Word.translation == word_to_delete)
        ).first()
        image = db_sess.query(Image).filter(Image.word_id == word.id).first()
        user = db_sess.query(User).filter(User.tg_id == request.from_user.id).first()

        if word and image and user:
            db_sess.delete(word)
            db_sess.delete(image)
            db_sess.commit()

            text = '✅ Успешно удалено.'
            await print_text(request, text)
            await state.clear()
        else:
            text = '⚠️ При удалении возникла ошибка. Попробуйте ещё раз.'
            await print_text(request, text)
            await state.clear()


# получение подтверждения от пользователя на очистку словаря
@delete_router.message(Command('clear_dict'))
@delete_router.callback_query(lambda c: c.data == "clear_dict")
async def get_confirm_by_user(request: Message | CallbackQuery, state: FSMContext):
    db_sess = db_session.create_session()
    user_id = request.from_user.id
    words = [user.words for user in db_sess.query(User).filter(User.tg_id == user_id).all()][0]
    if not words:
        text = '⚠️ Ваш словарь пуст! Вам нечего удалять!'
        await print_text(request, text)
    else:
        await state.set_state(Form.clear_dict)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Нет"), KeyboardButton(text="Да")]
            ], resize_keyboard=True
        )
        text = '❗ Очистка словаря является необратимым действием ❗\nВы уверены, что хотите очистить словарь?'
        await print_text(request, text, keyboard)


# полная очистка словаря
@delete_router.message(Form.clear_dict)
async def clear_dict(request: Message, state: FSMContext):
    user_answer = request.text
    if user_answer == 'Да':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.tg_id == request.from_user.id).first()

        for word in user.words:
            image = db_sess.query(Image).filter(Image.word_id == word.id).first()
            db_sess.delete(word)
            if image:
                db_sess.delete(image)

        db_sess.commit()
        text = '✅ Ваш словарь был успешно очищен!'
        await print_text(request, text, keyboard=ReplyKeyboardRemove())
        await state.clear()
    else:
        text = '✅ Очистка словаря была отменена.'
        await print_text(request, text, keyboard=ReplyKeyboardRemove())
        await state.clear()

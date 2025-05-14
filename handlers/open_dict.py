from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from data import db_session
from data.user import User

from utils.common import print_text


# Создаём роутер
open_dict_router = Router()


# просмотр всех слов
@open_dict_router.message(Command('open_dict'))
@open_dict_router.callback_query(lambda c: c.data == "open_dict")
async def process_add(request: Message | CallbackQuery):
    db_sess = db_session.create_session()
    user_id = request.from_user.id
    words = [user.words for user in db_sess.query(User).filter(User.tg_id == user_id).all()][0]
    if words:
        language = db_sess.query(User).filter(User.tg_id == user_id).first().language_preference
        text = "📚 Ваш словарь:\n\n"
        for word in words:
            text += (f'🔹 {word.original_word.capitalize()}({language}) → {word.translation.capitalize()}\n'
                     f'Добавлено: {word.added_date.strftime("%d.%m.%Y")}\n'
                     f'Последнее повторение: {word.last_reviewed.strftime("%d.%m.%Y")}\n\n')
        await print_text(request, text)
    else:
        text = "📚 Ваш словарь пуст! Добавляйте новые слова с помощью /add"
        await print_text(request, text)

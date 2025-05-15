from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from data import db_session
from data.user import User

from utils.common import print_text


# Создаём роутер
statistics_router = Router()


@statistics_router.message(Command('statistics'))
@statistics_router.callback_query(lambda c: c.data == "statistics")
async def process_add(message: Message):
    db_sess = db_session.create_session()
    user_id = message.from_user.id
    user = db_sess.query(User).filter(User.tg_id == user_id).first()
    language = db_sess.query(User).filter(User.tg_id == user_id).first().language_preference

    code_to_language = {
        'ru': 'Русский',
        'en': 'Английский',
        'zh': 'Китайский',
        'fr': 'Французский',
        'es': 'Испанский',
        'de': 'Немецкий',
        'pt': 'Португальский',
        'kk': 'Казахский'
    }

    language = code_to_language[language]

    text = (f'Моя статистика🤓\n\n'
            f'Пользователь: @{user.username}\n'
            f'Язык изучения: {language}\n'
            f'Лучший результат: {user.the_best_statistics}\n'
            f'Последний результат: {user.last_statistics}\n'
            f'Количество слов в словаре: {len(user.words)}\n\n'
            f'🚀Удачи в дальнейшем изучении!🚀')
    await print_text(message, text)
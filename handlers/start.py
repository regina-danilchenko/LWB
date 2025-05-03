from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext

from data import db_session
from data.user import User

from utils.states import Form


# Создаём роутер
start_router = Router()


# главное меню
@start_router.message(Command('start'))
async def process_start_command(message: Message, state: FSMContext):
    db_sess = db_session.create_session()
    users_ids = [user.tg_id for user in db_sess.query(User).all()]
    user_id = message.from_user.id
    if not user_id in users_ids:
        await state.set_state(Form.choice_language)
        keyboard_language = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Английский"), KeyboardButton(text="Китайский")],
                      [KeyboardButton(text="Французский"), KeyboardButton(text="Испанский")],
                      [KeyboardButton(text="Немецкий"),
                       KeyboardButton(text="Португальский")],
                      [KeyboardButton(text="Русский"), KeyboardButton(text="Казахский")]])

        await message.answer('Вы ещё не зарегестрированы.\n'
                             'Пройдите регистрацию и начинайте учить слова.\n\n'
                             'Выберите язык, на котром хотите учить слова.', reply_markup=keyboard_language)
    else:
        text = """
🌟Добро пожаловать в LearnWordsBot!🌟

Я помогу тебе:
✅ Расширить словарный запас
✅ Запоминать слова легко
✅ Преодолеть языковой барьер

С чего начнём? 🚀
Выбирай действие ниже! 👇
"""
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="➕ Добавить слово", callback_data="add"))
        builder.add(types.InlineKeyboardButton(text="📚 Словарь", callback_data="open_dict"))
        builder.add(types.InlineKeyboardButton(text="🎓 Учить", callback_data="learn"))
        builder.add(types.InlineKeyboardButton(text="📝 Проверка", callback_data="test"))
        builder.add(types.InlineKeyboardButton(text="❓ Помощь", callback_data="help"))
        builder.adjust(2)

        await message.answer(text, reply_markup=builder.as_markup())


# выбор языка, на котором будет проходить обучение, и регистрация
@start_router.message(Form.choice_language)
async def choice_language(message: Message, state: FSMContext):
    await state.clear()
    language = message.text
    language_to_code = {
        'Английский': 'en',
        'Китайский': 'zh',
        'Французский': 'fr',
        'Испанский': 'es',
        'Немецкий': 'de',
        'Португальский': 'pt',
        'Казахский': 'kk'
    }
    language_code = language_to_code.get(language)
    if not language_code:
        language_code = 'ru'

    db_sess = db_session.create_session()
    user = User()
    user.tg_id = message.from_user.id
    user.username = message.from_user.username
    user.language_preference = language_code
    user.statistics = 0
    db_sess.add(user)
    db_sess.commit()

    text = (f'✅ Вы, {message.from_user.username}, закончили регистрацию. ✅\n'
            '\n'
            'Начните изучение новых слов прямо сейчас.\n'
            '\n'
            '👍Желаем удачи!👍')
    await message.answer(text, reply_markup=ReplyKeyboardRemove())

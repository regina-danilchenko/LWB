import asyncio
import logging
from data.user import User
from data.word import Word
from data.image import Image
from data import db_session
from functions import translate
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import BotCommand, Message, CallbackQuery, ReplyKeyboardRemove
from config import BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
dp = Dispatcher()


class Form(StatesGroup):
    choice_language = State()
    add_word = State()
    add_image = State()


async def main():
    # инициализвция БД
    db_session.global_init("db/LearnWordsBD.db")
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_main_menu(bot)
    await dp.start_polling(bot)


# менюшка с командами бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='🚀 Запустить бота'),
        BotCommand(command='/add', description='➕ Добавить слово'),
        BotCommand(command='/open_dict', description='📚 Словарь'),
        BotCommand(command='/learn', description='🎓 Учить'),
        BotCommand(command='/test', description='📝 Проверка'),
        BotCommand(command='/help', description='❓ Помощь')
    ]
    await bot.set_my_commands(main_menu_commands)


# вывод текста
async def print_text(request, text, keyboard=None):
    if isinstance(request, CallbackQuery):
        if keyboard:
            await request.message.answer(text, reply_markup=keyboard)
        else:
            await request.message.answer(text)
        await request.answer()
    else:
        if keyboard:
            await request.answer(text, reply_markup=keyboard)
        else:
            await request.answer(text)


# главное меню
@dp.message(Command('start'))
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


# помощь
@dp.message(Command('help'))
@dp.callback_query(lambda c: c.data == "help")
async def process_help(request: Message | CallbackQuery):
    text = """
❓ Что умеет LearnWordsBot? ❓

➕ Добавлять слова (/add)
🎓 Учить с умным повторением (/learn)
📝 Проверять знания (/test)

И это только начало! 🚀
Используй кнопки меню или команды!
"""
    await print_text(request, text)


# команда добавления нового слова
@dp.message(Command('add'))
@dp.callback_query(lambda c: c.data == "add")
async def process_add(request: Message, state: FSMContext):
    await state.set_state(Form.add_word)
    text = 'Введите слово, которое хотите выучить.'
    await print_text(request, text)


# выбор языка, на котором будет проходить обучение, и регистрация
@dp.message(Form.choice_language)
async def choice_language(message: Message, state: FSMContext):
    await state.clear()
    language = message.text
    if language == 'Английский':
        language_code = 'en'
    elif language == 'Китайский':
        language_code = 'zh'
    elif language == 'Французский':
        language_code = 'fr'
    elif language == 'Испанский':
        language_code = 'es'
    elif language == 'Немецкий':
        language_code = 'de'
    elif language == 'Португальский':
        language_code = 'pt'
    elif language == 'Казахский':
        language_code = 'kk'
    else:
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


# добавление слова
@dp.message(Form.add_word)
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
    word.original_word = translated_word
    word.translation = original_word
    word.last_reviewed = datetime.now()
    db_sess.add(word)
    db_sess.commit()

    # добавление в словарь и добавление связи в таблицу связей user_to_word двух таблиц user и word
    db_sess = db_session.create_session()
    user_id = message.from_user.id
    user = db_sess.query(User).filter(User.tg_id == user_id).first()
    user.words.append(word)
    id_word = word.id
    user.statistics += 1
    db_sess.commit()

    # передача id слова в следующую функцию
    await state.update_data(id_word=id_word)
    await message.answer('Добавьте изображение к слову, чтобы лучше его запомнить.')


# добавление изображения и вывод результата
@dp.message(Form.add_image)
async def add_image(message: Message, state: FSMContext):
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
                         f'Дата добавленя: {datetime.now().strftime('%d.%m.%Y')}\n'
                         f'\n'
                         f'👍Так держать!👍')

    await message.answer_photo(photo=file_id, caption=text)


# просмотр всех слов
@dp.message(Command('open_dict'))
@dp.callback_query(lambda c: c.data == "open_dict")
async def process_add(request: Message | CallbackQuery):
    db_sess = db_session.create_session()
    user_id = request.from_user.id
    words = [user.words for user in db_sess.query(User).filter(User.tg_id == user_id).all()][0]
    language = db_sess.query(User).filter(User.tg_id == user_id).first().language_preference
    text = "📚 Ваш словарь:\n\n"
    for word in words:
        text += (f'🔹 {word.original_word.capitalize()}({language}) → {word.translation.capitalize()}\n'
                 f'Добавлено: {word.added_date.strftime('%d.%m.%Y')}\n'
                 f'Последнее повторение: {word.last_reviewed.strftime('%d.%m.%Y')}\n\n')
    await print_text(request, text)


# изучение слов
@dp.message(Command('learn'))
@dp.callback_query(lambda c: c.data == "learn")
async def process_learn(request: Message | CallbackQuery):
    text = "Функция изучения слов находится в разработке ⚙️"
    await print_text(request, text)


# проверка на знание слов
@dp.message(Command('test'))
@dp.callback_query(lambda c: c.data == "test")
async def process_test(request: Message | CallbackQuery):
    text = "Функция проверки на знание слов находится в разработке ⚙️"
    await print_text(request, text)


# реакция на сообщение от пользователя
# @dp.message()
# async def echo_message(message: Message):
#     text = "Я вижу твоё сообщение, но пока не могу его обработать 😞"
#     await message.answer(text)


if __name__ == '__main__':
    asyncio.run(main())
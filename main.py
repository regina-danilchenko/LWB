import asyncio
import logging
from data.user import User
from data.word import Word
from data import db_session
from functions import translate
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import BotCommand, Message, CallbackQuery, ReplyKeyboardRemove
from config import BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
dp = Dispatcher()

# глобальная переменная языка, на который будет переведено слово
language_code = None


class Form(StatesGroup):
    add = State()
    language = State()


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
async def process_start_command(message: Message):
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

    # добавление пользователя в БД, если его там нет
    db_sess = db_session.create_session()
    users_ids = [user.tg_id for user in db_sess.query(User).all()]
    user_id = message.from_user.id
    if not user_id in users_ids:
        user = User()
        user.tg_id = user_id
        db_sess.add(user)
        db_sess.commit()
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
    await state.set_state(Form.language)
    text = 'Выберите язык, на котором хотите выучить слово.'
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Английский"), KeyboardButton(text="Китайский")],
                                    [KeyboardButton(text="Французский"), KeyboardButton(text="Испанский")],
                                    [KeyboardButton(text="Немецкий"), KeyboardButton(text="Португальский")],
                                    [KeyboardButton(text="Русский"), KeyboardButton(text="Казахский")]])
    await print_text(request, text, keyboard=keyboard)


# выбор языка, на котором будет переведено слово
@dp.message(Form.language)
async def choice_language(message: Message, state: FSMContext):
    await state.set_state(Form.add)
    language = message.text
    global language_code
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

    text = 'Введите слово, которое хотите добавить.'
    await message.answer(text, reply_markup=ReplyKeyboardRemove())


# добавление и вывод результата
@dp.message(Form.add)
async def add_word(message: Message, state: FSMContext):
    global language_code
    await state.clear()
    original_word = message.text

    # перевод слова
    translated_word, original_language = translate(original_word.capitalize(), language_code)

    # добавление в словарь
    db_sess = db_session.create_session()
    word = Word()
    word.original_word = original_word
    word.translated_word = translated_word
    word.original_language = original_language
    word.target_language = language_code
    db_sess.add(word)
    db_sess.commit()

    # добавление в словарь и добавление связи в таблицу связей user_to_word двух таблиц user и word
    db_sess = db_session.create_session()
    user_id = message.from_user.id
    user = db_sess.query(User).filter(User.tg_id == user_id).first()
    user.words.append(word)
    db_sess.commit()
    
    await message.answer(f'Вы добавили в словарь новое слово!\n'
                         f'\n'
                         f'Слово: {original_word.capitalize()}\n'
                         f'Исходный язык: {original_language}\n'
                         f'Перевод: {translated_word}\n'
                         f'Язык перевода: {language_code}\n'
                         f'\n'
                         f'👍Так держать!👍')
    language_code = None



# просмотр всех слов
@dp.message(Command('open_dict'))
@dp.callback_query(lambda c: c.data == "open_dict")
async def process_add(request: Message | CallbackQuery):
    db_sess = db_session.create_session()
    user_id = request.from_user.id
    words = [user.words for user in db_sess.query(User).filter(User.tg_id == user_id).all()][0]
    text = "📚 Ваш словарь:\n\n"
    for word in words:
        text += (f'🔹 {word.original_word.capitalize()}({word.original_language}) → {word.translated_word}({word.target_language})\n'
                 f'Добавлено: {word.added_date.strftime('%d.%m.%Y')}\n\n')
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
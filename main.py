import asyncio
import logging


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
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_main_menu(bot)
    await dp.start_polling(bot)


# менюшка с командами бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='🚀 Запустить бота'),
        BotCommand(command='/add', description='➕ Добавить слово'),
        BotCommand(command='/learn', description='🎓 Учить'),
        BotCommand(command='/test', description='📝 Проверка'),
        BotCommand(command='/help', description='❓ Помощь')
    ]
    await bot.set_my_commands(main_menu_commands)


# вывод текста
async def print_text(request, text):
    if isinstance(request, CallbackQuery):
        await request.message.answer(text)
        await request.answer()
    else:
        await request.answer(text)


# главное меню
@dp.message(Command('start'))
async def process_start_command(message: Message):
    text = """
🌟 Добро пожаловать в LearnWordsBot! 🌟

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
async def process_add(message: Message, state: FSMContext):
    await state.set_state(Form.language)
    text = 'Выберите язык, на котором хотите выучить слово.'
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Английский"), KeyboardButton(text="Китайский")],
                                    [KeyboardButton(text="Французский"), KeyboardButton(text="Испанский")],
                                    [KeyboardButton(text="Немецкий"), KeyboardButton(text="Португальский")],
                                    [KeyboardButton(text="Русский"), KeyboardButton(text="Казахский")]])
    await message.answer(text, reply_markup=keyboard)


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
        print(language == 'Французский')

    text = 'Введите слово, которое хотите добавить.'
    await message.answer(text, reply_markup=ReplyKeyboardRemove())


# добавление и вывод результата
@dp.message(Form.add)
async def add_word(message: Message, state: FSMContext):
    global language_code
    await state.clear()
    word = message.text
    await message.answer(f'Вы добавили в словарь новое слово!\n'
                         f'\n'
                         f'Слово: {word.capitalize()}\n'
                         f'Исходный язык: {translate(word.capitalize(), language_code)[1]}\n'
                         f'Перевод: {translate(word.capitalize(), language_code)[0]}\n'
                         f'Язык перевода: {language_code}\n'
                         f'\n'
                         f'👍Так держать!👍')
    language_code = None



# просмотр всех слов
@dp.message(Command('open_dict'))
@dp.callback_query(lambda c: c.data == "open_dict")
async def process_add(request: Message | CallbackQuery):
    text = "Функция находится в разработке ⚙️"
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
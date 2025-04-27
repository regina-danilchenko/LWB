import asyncio
import logging


from functions import translate
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import BotCommand, Message, CallbackQuery
from config import BOT_TOKEN


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
dp = Dispatcher()


class Form(StatesGroup):
    add = State()


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


# добавление нового слова
@dp.message(Command('add'))
@dp.callback_query(lambda c: c.data == "add")
async def process_add(request: Message | CallbackQuery, state: FSMContext):
    await state.set_state(Form.add)
    text = "Введите слово, которое хотите добавить."
    await print_text(request, text)


@dp.message(Form.add)
async def add_word(message: Message, state: FSMContext):
    await state.clear()
    word = message.text
    await message.answer(f'Вы добавили в словарь новое слово!\n'
                         f'\n'
                         f'Слово: {word.capitalize()}\n'
                         f'Исходный язык: {translate(word.capitalize(), 'en')[1]}\n'
                         f'Перевод: {translate(word.capitalize(), 'en')[0]}\n'
                         f'Язык перевода: en\n'
                         f'\n'
                         f'👍Так держать!👍')



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

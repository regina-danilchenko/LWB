from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from utils.common import print_text


# Создаём роутер
help_router = Router()


# помощь
@help_router.message(Command('help'))
@help_router.callback_query(lambda c: c.data == "help")
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

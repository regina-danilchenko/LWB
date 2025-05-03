from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from utils.common import print_text


# Создаём роутер
test_router = Router()


# проверка на знание слов
@test_router.message(Command('test'))
@test_router.callback_query(lambda c: c.data == "test")
async def process_test(request: Message | CallbackQuery):
    text = "Функция проверки на знание слов находится в разработке ⚙️"
    await print_text(request, text)

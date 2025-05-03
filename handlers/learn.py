from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from utils.common import print_text


# Создаём роутер
learn_router = Router()


# изучение слов
@learn_router.message(Command('learn'))
@learn_router.callback_query(lambda c: c.data == "learn")
async def process_learn(request: Message | CallbackQuery):
    text = "Функция изучения слов находится в разработке ⚙️"
    await print_text(request, text)

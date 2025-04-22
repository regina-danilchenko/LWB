import asyncio
import logging


from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
dp = Dispatcher()


async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


@dp.message(Command('start'))
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nЯ бот для изучения иностранных слов📚")


@dp.message(Command('help'))
async def process_help_command(message: types.Message):
    await message.reply("Пока что я умею только здороваться😞")


@dp.message()
async def echo_message(message: types.Message):
    await message.answer('Я вижу твоё сообщение, но пока не могу его обработать😞')


if __name__ == '__main__':
    asyncio.run(main())

import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from data import db_session
from handlers import routers
from menu.main_menu import set_main_menu


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
dp = Dispatcher()


async def main():
    # инициализвция БД
    db_session.global_init("db/LearnWordsBD.db")

    # Конфигурация бота
    bot = Bot(token=BOT_TOKEN)

    # Подключение роутеров
    for router in routers:
        dp.include_router(router)

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await set_main_menu(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

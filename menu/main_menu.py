from aiogram import Bot
from aiogram.types import BotCommand


# менюшка с командами бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='🚀 Запустить бота'),
        BotCommand(command='/add', description='➕ Добавить слово'),
        BotCommand(command='/delete', description='❌ Удалить слово'),
        BotCommand(command='/open_dict', description='📚 Словарь'),
        BotCommand(command='/clear_dict', description='🚫 Очистить словарь'),
        BotCommand(command='/learn', description='🎓 Учить'),
        BotCommand(command='/test', description='📝 Проверка'),
        BotCommand(command='/statistics', description='🤓 Моя статистика'),
        BotCommand(command='/help', description='❓ Помощь')
    ]
    await bot.set_my_commands(main_menu_commands)

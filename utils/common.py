from aiogram.types import CallbackQuery


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

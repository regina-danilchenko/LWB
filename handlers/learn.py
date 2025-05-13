import os
import random

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from data import db_session
from data.image import Image
from data.user import User

from utils.common import print_text
from utils.states import Form


# Создаём роутер
learn_router = Router()

# глобальные переменные
visited = 0
db_sess = None


# выбор режима изучения слов
@learn_router.message(Command('learn'))
@learn_router.callback_query(lambda c: c.data == "learn")
async def process_learn(request: Message | CallbackQuery):
    global db_sess
    db_sess = db_session.create_session()
    user_id = request.from_user.id
    words = [user.words for user in db_sess.query(User).filter(User.tg_id == user_id).all()][0]

    if len(words) < 5:
        text = "В вашем словаре слишком мало слов! Добавьте новые слова с помощью /add"
        await print_text(request, text)
        return

    text = "Выбери режим изучения слов 👇"
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🖼️ Показ карточек", callback_data="show_cards"))
    builder.add(types.InlineKeyboardButton(text="🎯 Сопоставь слово с картинкой", callback_data="word_to_card_game"))
    builder.add(types.InlineKeyboardButton(text="🤔 Угадай перевод слова", callback_data="guess_word_translation_game"))
    builder.add(types.InlineKeyboardButton(
        text="💡 Выбери правильный вариант перевода",callback_data="choose_word_translation_game"
    ))
    builder.adjust(1)

    await print_text(request, text, builder.as_markup())


# показ карточек
@learn_router.callback_query(lambda c: c.data == "show_cards")
async def show_cards(request: CallbackQuery):
    global db_sess
    user_id = request.from_user.id
    words = [user.words for user in db_sess.query(User).filter(User.tg_id == user_id).all()][0]
    global visited

    if visited == len(words):
        visited = 0
        text = "🎉 Вы просмотрели все карточки!"
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="🔄 Начать заново",
            callback_data="show_cards"
        ))
        builder.add(types.InlineKeyboardButton(
            text="🏠 Вернуться в главное меню",
            callback_data="start"
        ))
        builder.adjust(1)
        await request.message.delete()
        await request.message.answer(text, reply_markup=builder.as_markup())
    else:
        await show_one_card(words[visited], request)
        visited += 1


# вспомогательная функция дял показа карточек
async def show_one_card(current_word, request):
    global db_sess
    original_word = current_word.original_word
    translation = current_word.translation

    text = f"Слово: {original_word.capitalize()}\nПеревод: {translation.capitalize()}"
    image = db_sess.query(Image).filter(Image.word_id == current_word.id).first()

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="⏭️ Следующая карточка", callback_data="show_cards"))

    if image:
        await request.message.edit_media(
            InputMediaPhoto(media=image.file_id,caption=text), reply_markup=builder.as_markup()
        )
    else:
        photo = types.FSInputFile(os.path.join('static', 'images', 'no_image.png'))
        await request.message.edit_media(
            InputMediaPhoto(media=photo, caption=text), reply_markup=builder.as_markup()
        )

    await request.answer()


# сопоставление слова с картинкой
@learn_router.callback_query(lambda c: c.data == "word_to_card_game")
async def word_to_card_game(request: CallbackQuery):
    text = "Функция находится в разработке ⚙️"
    await print_text(request, text)


# угадать перевод слова
@learn_router.callback_query(lambda c: c.data == "guess_word_translation_game")
async def guess_word_translation_game(request: CallbackQuery, state: FSMContext):
    global db_sess
    user_id = request.from_user.id
    words = [user.words for user in db_sess.query(User).filter(User.tg_id == user_id).all()][0]
    word = random.choice(words)

    prompt_variants = [
        f"Слово: {word.translation}\nУгадай перевод и напиши его ниже 👇\nЕсли вдруг не получится — напиши /stop",
        f"Перевод какого слова: {word.translation}?\nВведи ответ ниже 👇\nЕсли захочешь выйти — команда /stop",
        f"Попробуй перевести: {word.translation}\nЖду твой ответ 👇\nЧтобы закончить — введи /stop",
        f"Значение: {word.translation}\nКак это звучит на другом языке?\nОтвет ниже 👇 или /stop для выхода",
        f"Вот слово: {word.translation}\nВведи перевод ниже 👇\nЕсли нужно прерваться — напиши /stop",
        f"Переведи слово: {word.translation}\nПиши свой вариант 👇\nДля остановки — /stop",
        f"Что означает «{word.translation}» на изучаемом языке?\nОтвет напиши ниже 👇\nДля выхода — /stop"
    ]

    await state.set_state(Form.guess_translation)
    await state.update_data(correct_answer=word.original_word)
    await print_text(request, random.choice(prompt_variants))


# проверка, угадал ли пользователь перевод
@learn_router.message(Form.guess_translation)
async def check_correct_guess(request: Message, state: FSMContext):
    user_answer = request.text
    data = await state.get_data()
    wrong_variants = [
        "Не угадали 😞. Попробуйте ещё раз!",
        "Увы, мимо! Но вы справитесь 💪",
        "Не то слово... Ещё попытка?",
        "Почти! Но пока нет. Дальше будет лучше!",
        "Не получилось сейчас — получится в следующий раз!",
        "Неправильно 😕. Давайте ещё подумаем!",
        "Эх, не то! Но вы точно на верном пути!"
    ]
    success_variants = [
        "Верно! 🎉 Отличная работа!",
        "Угадали! 🔥 Так держать!",
        "Браво! 💡 Вы на волне!",
        "Точно! 👍 Продолжайте в том же духе!",
        "Правильно! 🏆 Вы молодец!",
        "Есть контакт! ✅ Следующее слово ждёт!",
        "Отгадано! 🎯 Вы справились!"
    ]
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="⏭️ Дальше",
        callback_data="guess_word_translation_game"
    ))
    builder.add(types.InlineKeyboardButton(
        text="🏠 Вернуться в главное меню",
        callback_data="start"
    ))
    builder.adjust(1)

    if user_answer == '/stop':
        text = f'Правильным ответом был: {data['correct_answer']}'
        await state.clear()
        await print_text(request, text, builder.as_markup())
    elif data['correct_answer'] == user_answer.capitalize():
        await state.clear()
        await print_text(request, random.choice(success_variants), builder.as_markup())
    else:
        await print_text(request, random.choice(wrong_variants))


# выбрать правильный перевод
@learn_router.callback_query(lambda c: c.data == "choose_word_translation_game")
async def choose_word_translation_game(request: CallbackQuery):
    text = "Функция находится в разработке ⚙️"
    await print_text(request, text)

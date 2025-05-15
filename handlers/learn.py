import os
import logging
from random import shuffle
import random

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from data import db_session
from data.image import Image
from data.user import User
from data.word import Word

from utils.common import print_text
from utils.states import Form


# Настройка логгера
logger = logging.getLogger(__name__)

# Создаём роутер
learn_router = Router()

# глобальные переменные
visited = 0
db_sess = None
current_image_index = 0
current_game_round = {}
MAX_ROUNDS = 5
correct_answers = 0


# Получение слов пользователя
async def get_user_words(user_id):
    global db_sess
    user = db_sess.query(User).filter(User.tg_id == user_id).first()
    return user.words if user else []


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
    global current_game_round
    user_id = request.from_user.id
    current_game_round[user_id] = 1
    await word_to_card_game_logic(user_id, request.message)


# логика игры "сопоставь слово с картинкой"
async def word_to_card_game_logic(user_id: int, message: Message):
    session = db_session.create_session()
    try:
        user = session.query(User).filter(User.tg_id == user_id).first()
        if not user or not user.words:
            await message.answer("У вас нет слов для изучения.")
            return

        words_with_images = (
            session.query(Word)
            .join(Image)
            .filter(Word.id.in_([w.id for w in user.words]))
            .all()
        )
        if len(words_with_images) < 4:
            await message.answer("Недостаточно слов с картинками для игры.")
            return

        shuffle(words_with_images)
        game_words = words_with_images[:4]
        correct_word = game_words[0]

        images = session.query(Image).filter(Image.word_id == correct_word.id).all()
        if not images:
            await message.answer("У этого слова нет картинок.")
            return

        shuffle(images)
        image = images[0]

        builder = InlineKeyboardBuilder()
        for word in game_words:
            builder.button(
                text=word.original_word,  # Показываем оригинальное слово (например, английское)
                callback_data=f"wcard_ans_{word.id}_{correct_word.id}_{user_id}"
            )
        builder.adjust(2)

        await message.answer_photo(
            photo=image.file_id,
            caption=f"Раунд {current_game_round.get(user_id, 1)} из {MAX_ROUNDS}.\nВыберите правильный перевод:",
            reply_markup=builder.as_markup()
        )
    finally:
        session.close()


# обработка ответа на карточку
@learn_router.callback_query(lambda c: c.data.startswith("wcard_ans_"))
async def check_word_card_answer(callback: CallbackQuery):
    global current_game_round, correct_answers
    session = db_session.create_session()
    try:
        _, _, selected_id, correct_id, user_id = callback.data.split("_")
        selected_id = int(selected_id)
        correct_id = int(correct_id)
        user_id = int(user_id)

        if selected_id == correct_id:
            user = session.query(User).filter(User.tg_id == user_id).first()
            if user:
                user.statistics = (user.statistics or 0) + 1
                session.commit()

            correct_answers += 1
            await callback.answer("Правильно! ✅", show_alert=True)
        else:
            correct_word = session.query(Word).get(correct_id)
            correct_translation = correct_word.translation  # Правильный перевод
            original_word = correct_word.original_word  # Оригинальное слово
            await callback.answer(f"Неправильно! ❌\nПравильный ответ: {original_word} - {correct_translation}", show_alert=True)



        await callback.message.delete()

        # Следующий раунд или конец игры
        current_round = current_game_round.get(user_id, 1)
        if current_round < MAX_ROUNDS:
            current_game_round[user_id] = current_round + 1
            await word_to_card_game_logic(user_id, callback.message)
        else:
            current_game_round[user_id] = 1
            kb = InlineKeyboardBuilder()
            kb.add(types.InlineKeyboardButton(
                text="🔄 Начать заново",
                callback_data="word_to_card_game"
            ))
            kb.add(types.InlineKeyboardButton(
                text="🏠 Вернуться в главное меню",
                callback_data="start"
            ))
            kb.adjust(1)

            result_text = f"Ваш результат: {correct_answers} из {MAX_ROUNDS}."
            await callback.message.answer(f"Игра окончена! 🎉\n{result_text}", reply_markup=kb.as_markup())

            correct_answers = 0

    except Exception as e:
        logger.error(f"Error in check_word_card_answer: {e}", exc_info=True)
        await callback.answer("Произошла ошибка", show_alert=True)
    finally:
        session.close()


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
        text = f'Правильным ответом был: {data["correct_answer"]}'
        await state.clear()
        await print_text(request, text, builder.as_markup())
    elif data['correct_answer'] == user_answer.capitalize():
        await state.clear()
        await print_text(request, random.choice(success_variants), builder.as_markup())
    else:
        await print_text(request, random.choice(wrong_variants))

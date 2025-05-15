from random import choice

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup

from data import db_session
from data.user import User
from data.word import Word

from utils.common import print_text
from utils.states import Form


# Создаём роутер
test_router = Router()

#
score = 0
tests = 0
all_tests = 0

@test_router.message(Command('test'))
@test_router.callback_query(lambda c: c.data == "test")
async def process_add(request: Message, state: FSMContext):
    global all_tests, tests, score
    await state.set_state(Form.write_translation)
    text = ('Пройдите тест и узнайте сколько слов \n'
            'Вы выучили из своего словаря. \n\n'
            'В тесте представлено несколько режимов проверки знания слов.\n'
            'Следуйте инструкциям и выберайте правильные значения.\n\n'
            'Чтобы принудительно завершить тест\n'
            'Нажмите /stop.')
    db_sess = db_session.create_session()
    user_id = request.from_user.id
    original_words = [word.original_word for word in db_sess.query(User).filter(User.tg_id == user_id).first().words]
    all_tests = len(original_words)
    tests = 0
    score = 0
    await state.update_data(original_words=original_words, true_word=None, r=0)
    await print_text(request, text, ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Начать тест')],
                                                         [KeyboardButton(text='/stop')]]))

@test_router.message(Command('stop'))
async def close(message: Message, state: FSMContext):
    global all_tests, tests, score
    data = await state.get_data()
    if data["r"] > 0:
        get_answer(data["true_word"], message.text, data['r'])
    text = ('Вы принудительно завершили тест.\n\n'
            f'Вы прошли {tests} тестов из {all_tests}.\n'
            f'И набрали {score} баллов из {all_tests}.\n\n'
            '1 тест - 1 балл.\n\n')
    wrong_variants = [
        'Хороший результат.',
        'Есть к чему стремиться.',
        'Почти! Но пока нет.',
        'Попробуйте ещё раз!',
        'Дальше будет лучше!',
        'В следующий раз будет лучше!'
    ]
    text += choice(wrong_variants)
    await print_text(message, text, ReplyKeyboardRemove())


@test_router.message(Form.end)
async def end(message: Message, state: FSMContext):
    data = await state.get_data()
    if data["r"] > 0:
        get_answer(data["true_word"], message.text, data['r'])
    await state.clear()
    global all_tests, tests, score
    text = ('Вы звершили прохождение теста.\n\n'
            f'Вы прошли {tests} тестов из {all_tests}.\n'
            f'И набрали {score} баллов из {all_tests}.\n\n'
            '1 тест - 1 балл.\n\n')
    success_variants = [
        'Так держать!',
        'Молодец!',
        'Превосходно!',
        'В следующий раз будет ещё лучше!',
        'Вы отлично справились!',
        'Вы просто огонь!'
    ]
    wrong_variants = [
        'Хороший результат.',
        'Есть к чему стремиться.',
        'Почти! Но пока нет.',
        'Попробуйте ещё раз!',
        'Дальше будет лучше!',
        'В следующий раз будет лучше!'
    ]
    if score == all_tests:
        text += choice(success_variants)
    else:
        text += choice(wrong_variants)
    await print_text(message, text, ReplyKeyboardRemove())


def get_answer(true_word, word, r):
    global score, tests
    db_sess = db_session.create_session()

    if int(r) == 1:
        translation_true_word = db_sess.query(Word).filter(Word.original_word == true_word).first().translation
        if word.capitalize() == translation_true_word.capitalize():
            score += 1
    elif int(r) == 2:
        if word.capitalize() == true_word.capitalize():
            score += 1
    elif int(r) == 3:
        if word.capitalize() == true_word.capitalize():
            score += 1
    tests += 1

# добавление слова
@test_router.message(Form.write_translation)
async def write_translation(message: Message, state: FSMContext):
    global tests, score
    data = await state.get_data()

    original_words = data["original_words"]
    true_word = data["true_word"]
    if message.text == '/stop':
        await state.clear()
        return
    elif message.text == 'Начать тест' and data['true_word'] is None:
        ...
    else:
        word = message.text
        get_answer(true_word, word, 3)

    true_word = choice(original_words)
    original_words.remove(true_word)
    text = f'Напишите перевод слова "{true_word}".'

    if not original_words:

        await state.set_state(Form.end)
    else:
        await state.set_state(Form.write_original)
    await state.update_data(original_words=original_words, true_word=true_word, r=1)
    await print_text(message, text, ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/stop')]]))


@test_router.message(Form.write_original)
async def write_original(message: Message, state: FSMContext):
    data = await state.get_data()
    db_sess = db_session.create_session()

    original_words = data["original_words"]
    true_word = data["true_word"]

    if message.text == '/stop':
        await state.clear()
        return
    else:
        word = message.text
        get_answer(true_word, word, 1)

    true_word = choice(original_words)
    original_words.remove(true_word)
    translation_true_word = db_sess.query(Word).filter(Word.original_word == true_word).first().translation
    text = f'Наипишите, какое слово переводится как "{translation_true_word}".'

    if not original_words:
        await state.set_state(Form.end)
    else:
        await state.set_state(Form.choice_translation)
    await state.update_data(original_words=original_words, true_word=true_word, r=2)
    await print_text(message, text)


@test_router.message(Form.choice_translation)
async def choice_translation(message: Message, state: FSMContext):
    db_sess = db_session.create_session()
    user_id = message.from_user.id

    data = await state.get_data()
    original_words = data["original_words"]
    true_word = data["true_word"]

    if message.text == '/stop':
        await state.clear()
        return
    else:
        word = message.text
        get_answer(true_word, word, 2)

    true_word = choice(original_words)
    original_words.remove(true_word)
    translation_true_word = db_sess.query(Word).filter(Word.original_word == true_word).first().translation

    keyboard = list()
    words = [word.original_word for word in db_sess.query(User).filter(User.tg_id == user_id).first().words]
    words.remove(true_word)
    # определяем кол-во слов в клавиатуре
    if len(words) >= 9:
        n = 9
    else:
        n = len(words)

    # выбираем случайные слова для клавиатуры
    words_for_keyboard = [true_word]
    for _ in range(n - 1):
        word_for_keyboard = choice(words)
        words.remove(word_for_keyboard)
        words_for_keyboard.append(word_for_keyboard)

    # добавляем слова в клавиатуру
    for i in range(0, n, 3):
        line_of_words = list()
        word = choice(words_for_keyboard)
        words_for_keyboard.remove(word)
        line_of_words.append(KeyboardButton(text=word))
        if i + 1 < n:
            word = choice(words_for_keyboard)
            words_for_keyboard.remove(word)
            line_of_words.append(KeyboardButton(text=word))
        if i + 2 < n:
            word = choice(words_for_keyboard)
            words_for_keyboard.remove(word)
            line_of_words.append(KeyboardButton(text=word))
        keyboard.append(line_of_words)

    keyboard_words = ReplyKeyboardMarkup(keyboard=keyboard)
    text = f'Выбери слово, перевод которого "{translation_true_word}".'

    if not original_words:
        await state.set_state(Form.end)
    else:
        await state.set_state(Form.write_translation)
    await print_text(message, text, keyboard_words)
    await state.update_data(original_words=original_words, true_word=true_word, r=3)
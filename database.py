import sqlite3
from sqlite3 import Error


# Создает соединение с базой данных SQLite
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("words.db")
        print(f"Подключение к SQLite успешно, версия SQLite: {sqlite3.version}")
        return conn
    except Error as e:
        print(f"Ошибка при подключении к SQLite: {e}")
    return conn


# Создает таблицу для хранения слов
def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_word TEXT NOT NULL,
            translated_word TEXT NOT NULL,
            original_language TEXT NOT NULL,
            target_language TEXT NOT NULL,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )
        conn.commit()
        print("Таблица words создана успешно")
    except Error as e:
        print(f"Ошибка при создании таблицы: {e}")


# Добавляет новое слово в базу данных
def insert_word(
    conn, original_word, translated_word, original_language, target_language
):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
        INSERT INTO words (original_word, translated_word, original_language, target_language)
        VALUES (?, ?, ?, ?)
        """,
            (original_word, translated_word, original_language, target_language),
        )
        conn.commit()
        print("Слово успешно добавлено в базу данных")
        return cursor.lastrowid
    except Error as e:
        print(f"Ошибка при добавлении слова: {e}")
        return None


# Получает все слова из базы данных
def get_all_words(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM words")
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"Ошибка при получении слов: {e}")
        return []


# Инициализация базы данных при импорте
conn = create_connection()
if conn is not None:
    create_table(conn)
else:
    print("Ошибка! Не удалось подключиться к базе данных.")

import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


# модель таблицы Word в БД
class Word(SqlAlchemyBase):
    __tablename__ = 'words'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    original_word = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    translated_word = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    original_language = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    target_language = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    added_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

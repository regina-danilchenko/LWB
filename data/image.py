import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


# модель таблицы Image в БД
class Image(SqlAlchemyBase):
    __tablename__ = 'images'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    word_id  = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('words.id'))
    file_id = sqlalchemy.Column(sqlalchemy.Integer)

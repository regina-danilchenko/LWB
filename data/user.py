import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# модель таблицы User в БД
class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    tg_id =sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    words = orm.relationship("Word",
                                  secondary="user_to_word",
                                  backref="users")


# таблица связей(многое-ко-многим)
association_table = sqlalchemy.Table(
    'user_to_word',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('users', sqlalchemy.Integer,sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('words', sqlalchemy.Integer,sqlalchemy.ForeignKey('words.id')))

import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# модель таблицы User в БД
class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    tg_id = sqlalchemy.Column(sqlalchemy.Integer)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    language_preference = sqlalchemy.Column(sqlalchemy.String)
    the_best_statistics = sqlalchemy.Column(sqlalchemy.String, default='0/0')
    last_statistics = sqlalchemy.Column(sqlalchemy.String, default='0/0')
    words = orm.relationship("Word",
                                  secondary="user_to_word",
                                  backref="users")


# таблица связей(многое-ко-многим)
association_table = sqlalchemy.Table(
    'user_to_word',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('users', sqlalchemy.Integer,sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('words', sqlalchemy.Integer,sqlalchemy.ForeignKey('words.id')))

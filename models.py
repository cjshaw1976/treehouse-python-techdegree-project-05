import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('tasks.db')


class Task(Model):
    title = CharField(unique=True)
    date = DateField(default=datetime.date.today)
    time_spent = IntegerField(default=0)
    what_i_learned = TextField()
    resources_to_remember = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-date',)

    def get_tags(self):
        return Tags.select().where(Tags.task == self)


class Tags(Model):
    name = CharField()
    task = ForeignKeyField(Task, related_name='to_tag')

    class Meta:
        database = DATABASE
        primary_key = CompositeKey('name', 'task')


class User(UserMixin, Model):
    username = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE
        order_by = ('username',)

    @classmethod
    def new(cls, username, password):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    password=generate_password_hash(password))
        except IntegrityError:
            raise ValueError("User already exists")


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Task, Tags, User], safe=True)
    DATABASE.close()

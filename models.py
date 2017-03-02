import datetime

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


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Task], safe=True)
    DATABASE.close()

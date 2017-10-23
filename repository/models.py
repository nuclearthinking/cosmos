from peewee import *

db = SqliteDatabase('cosmos.db')


class Session(Model):
    creation_date_time = DateTimeField()
    las_activity_date_time = DateTimeField()
    user = ForeignKeyField(User)


class User(Model):
    user_id = IntegerField()
    username = CharField()
    points = IntegerField()



from peewee import *

db = SqliteDatabase('cosmos.db')


class User(Model):
    user_id = IntegerField()
    username = CharField()
    points = IntegerField(null=True)

    class Meta:
        database = db

class Session(Model):
    creation_date_time = DateTimeField()
    las_activity_date_time = DateTimeField()
    user = ForeignKeyField(User)

    class Meta:
        database = db




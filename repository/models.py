from peewee import *

db = SqliteDatabase('cosmos.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField()
    username = CharField()
    points = IntegerField(null=True)


class File(BaseModel):
    id = PrimaryKeyField()
    path = CharField()
    telegram_id = CharField()
    hash_string = CharField()


class Vote(BaseModel):
    id = PrimaryKeyField()
    publication_id = IntegerField()
    user = ForeignKeyField(User)
    date = DateTimeField()


class Publication(BaseModel):
    id = PrimaryKeyField()
    creation_date = DateTimeField()
    publishing_date = DateTimeField()
    votes = ForeignKeyField(Vote)
    published = BooleanField()

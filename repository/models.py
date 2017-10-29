from peewee import *

db = SqliteDatabase('cosmos.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = PrimaryKeyField()
    user_id = IntegerField(unique=True)
    username = CharField(unique=True)
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
    points = IntegerField(default=0)


class Publication(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, null=False)
    item = ForeignKeyField(File, null=False)
    creation_date = DateTimeField(null=False)
    publishing_date = DateTimeField(null=True)
    votes = ForeignKeyField(Vote, null=True)
    score = FloatField(null=True)
    published = BooleanField(null=True)
    message_id = IntegerField(null=True)

from _thread import RLock
import threading

import psycopg2
from peewee import *

db = PostgresqlDatabase('cosmos', user='cosmos', password="cosmos", threadlocals=True, use_speedups=True,
                        autorollback=True)
db.connect()

db_lock = threading.Lock()


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = PrimaryKeyField()
    user_id = IntegerField(unique=True)
    username = CharField(unique=True)
    points = IntegerField(null=True)

class Contributor(BaseModel):
    id = PrimaryKeyField()
    user_id = IntegerField(unique=True)
    username = CharField(unique=True)
    points = IntegerField(null=True, default=0)


class Moderator(BaseModel):
    id = PrimaryKeyField()
    user_id = IntegerField(unique=True)
    username = CharField(unique=True)
    points = IntegerField(null=True, default=0)


class File(BaseModel):
    id = PrimaryKeyField()
    path = CharField()
    telegram_id = CharField(null=True)
    hash_string = CharField()
    image_dhash = CharField()
    image_ahash = CharField()
    image_phash = CharField()
    image_whash = CharField()


class Vote(BaseModel):
    id = PrimaryKeyField()
    publication_id = IntegerField()
    user = ForeignKeyField(User)
    date = DateTimeField()
    points = IntegerField(default=0)
    moderator = ForeignKeyField(Moderator, to_field=Moderator.id)


class ParsingSource(BaseModel):
    id = PrimaryKeyField()
    domain = CharField()
    parsed_posts = IntegerField(default=0)


class VkPhoto(BaseModel):
    id = PrimaryKeyField()
    rnd = IntegerField()
    photo_id = IntegerField(unique=True)
    owner_id = IntegerField()
    processed = BooleanField(default=False)


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
    moderated = BooleanField(null=True)
    contributor = ForeignKeyField(Contributor, to_field=Contributor.id)

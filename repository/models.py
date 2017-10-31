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

    def __repr__(self):
        return f'id = {self.id}, user = {self.user}, item = {self.item}, creation_date = {self.creation_date}, publishing_date = {self.publishing_date},\n' \
               f'votes = {self.votes}, score = {self.score}, published = {self.published}, message_id = {self.message_id}'

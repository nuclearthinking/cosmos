from playhouse.migrate import *

from repository.models import *

migrator = PostgresqlMigrator(db)

operations = [
    migrator.add_column('vote', 'moderator_id', ForeignKeyField(Moderator, to_field=Moderator.id, default=1)),
    migrator.add_column('publication', 'contributor_id',
                        ForeignKeyField(Contributor, to_field=Contributor.id, default=1))
]


def preform_migration(operations_to_preform: []):
    """
    Preform migrations from list ``operations_to_perform``
    :param operations_to_preform: ``migrator.operation``
    :return:
    """
    for item in operations_to_preform:
        try:
            item.run()
        except (OperationalError, ProgrammingError):
            pass


db.create_tables([Moderator, Contributor], safe=True)

users = [
    {'user_id': 6897745, 'username': 'nuclearthinking', 'points': 0},
    {'user_id': 57071745, 'username': 'GiantBurrito', 'points': 0},
    {'user_id': 132574151, 'username': 'Murchick', 'points': 0},
    {'user_id': 317098093, 'username': 'outbreakltd', 'points': 0}
]
try:
    Moderator.insert_many(users).execute()
except:
    pass
users.append({'user_id': 1, 'username': 'system', 'points': 0})
try:
    Contributor.insert_many(users).execute()
except:
    pass
preform_migration(operations)
for publication in Publication.select():
    contributor = Contributor.select().where(Contributor.username == publication.user.username)
    publication.contributor = contributor
for vote in Vote.select():
    moderator = Moderator.select().where(Moderator.username == vote.user.username)
    vote.moderator = moderator

second_operations = [
    migrator.drop_column('publication', 'user_id', cascade=False),
    migrator.drop_column('vote', 'user_id', cascade=False),
    migrator.rename_table('users', 'deprecated_users')
]
preform_migration(second_operations)

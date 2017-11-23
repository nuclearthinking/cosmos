from playhouse.migrate import *

from repository.models import *

migrator = PostgresqlMigrator(db)

operations = [
    migrator.add_column('moderator', 'password', CharField(null=True)),
    migrator.drop_not_null('moderator', 'user_id'),
    migrator.drop_not_null('moderator', 'username')
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


preform_migration(operations)

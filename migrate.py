from playhouse.migrate import *

from repository.models import *

migrator = PostgresqlMigrator(db)

from passlib.hash import pbkdf2_sha256

hash_pass = pbkdf2_sha256.hash("12345")

operations = [
    migrator.add_column('moderator', 'password', CharField(default=hash_pass)),
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

from playhouse.migrate import *

from repository.models import *

migrator = PostgresqlMigrator(db)

operations = [
    migrator.add_column('publication', 'deleted', BooleanField(null=True))
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

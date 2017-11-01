from playhouse.migrate import *

from repository.models import *

db.create_tables([User, File, Publication, Vote, ParsingSource, ParsedItem], safe=True)

migrator = SqliteMigrator(db)

migrations = [
    migrator.add_column('file', 'vk_id', IntegerField(null=True)),
    migrator.add_column('file', 'vk_owner', IntegerField(null=True)),
    migrator.add_column('file', 'fingerprint', CharField(null=True))
]

for migration in migrations:
    try:
        migration.run()
    except OperationalError:
        pass

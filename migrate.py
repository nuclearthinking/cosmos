from playhouse.migrate import *

from repository.models import *
from service import image_service

migrator = SqliteMigrator(db)

operations = [
    migrator.add_column('file', 'image_dhash', CharField(null=True)),
    migrator.add_column('file', 'image_ahash', CharField(null=True)),
    migrator.add_column('file', 'image_phash', CharField(null=True)),
    migrator.add_column('file', 'image_whash', CharField(null=True)),
    migrator.add_column('file', 'source', CharField(null=True))
]

# execute migrations
for item in operations:
    try:
        item.run()
    except OperationalError:
        pass


def hash_all_files():
    for file in File.select().where((File.image_ahash == None) | (File.image_dhash == None) |
                                            (File.image_phash == None) | (File.image_whash == None)):
        hashes = image_service.get_image_hashes(file.path)
        file.image_dhash = hashes.get('dHash')
        file.image_ahash = hashes.get('aHash')
        file.image_phash = hashes.get('pHash')
        file.image_whash = hashes.get('wHash')
        file.save()


if File.select().where((File.image_ahash == None) | (File.image_dhash == None) |
                               (File.image_phash == None) | (File.image_whash == None)).exists():
    hash_all_files()

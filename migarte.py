from playhouse.migrate import *

from repository.models import *
from service import image_service

migrator = SqliteMigrator(db)

operations = [
    migrator.add_column('file', 'image_hash', CharField(null=True)),
    migrator.add_column('file', 'image_dhash', CharField(null=True)),
    migrator.add_column('file', 'image_ahash', CharField(null=True)),
    migrator.add_column('file', 'image_phash', CharField(null=True)),
    migrator.add_column('file', 'image_whash', CharField(null=True))
]

# execute migrations
for item in operations:
    try:
        item.run()
    except OperationalError:
        pass


def hash_all_files():
    for file in File.select():
        hashes = image_service.get_image_hashes(file.path)
        file.image_dhash = hashes.get('dhash')
        file.image_ahash = hashes.get('ahash')
        file.image_phash = hashes.get('phash')
        file.image_whash = hashes.get('whash')
        file.save()


def find_all_similar():
    for file in File.select():
        image_service.find_similar_images(file)


hash_all_files()  # hash all unhashed files
find_all_similar()
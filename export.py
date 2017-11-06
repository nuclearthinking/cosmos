import json
import logging

from migration import sql
from repository.models import *

logger = logging.getLogger(__name__)

db.create_tables([File, User, Publication, Vote],safe=True)
logger.debug('Starting fetching files data')
files = []
for file in sql.File.select():
    files.append({
        'id': file.id,
        'path': file.path,
        'telegram_id': file.telegram_id,
        'hash_string': file.hash_string,
        'image_dhash': file.image_dhash,
        'image_ahash': file.image_ahash,
        'image_phash': file.image_phash,
        'image_whash': file.image_whash,
        'source': 'tg'
    })
logger.debug('Files data successfully fetched')
logger.debug('Starting importing fetched data')
try:
    File.insert_many(files).execute()
except Exception:
    pass

users = []
for user in sql.User.select():
    users.append(
        {'id': user.id,
         'user_id': user.user_id,
         'username': user.username,
         'points': user.points}
    )
try:
    User.insert_many(users).execute()
except Exception:
    pass

logger.debug('Fetching publications')
publications = []
for publication in sql.Publication.select():
    publications.append(
        {
            'id': publication.id,
            'user': publication.user,
            'item': publication.item,
            'creation_date': publication.creation_date,
            'publishing_date': publication.publishing_date,
            'votes': publication.votes,
            'score': publication.score,
            'published': publication.published,
            'message_id': publication.message_id,
            'moderated': publication.moderated
        }
    )

logger.debug('Inserting new data to database')
try:
    Publication.insert_many(publications).execute()
except Exception:
    pass

votes = []

for vote in sql.Vote.select():
    votes.append(
        {
            'id': vote.id,
            'publication_id': vote.publication_id,
            'user': vote.user,
            'date': vote.date,
            'points': vote.points,
        }
    )
try:
    Vote.insert_many(votes).execute()
except:
    pass

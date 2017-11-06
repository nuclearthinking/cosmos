import logging
from datetime import timedelta

import time
from threading import Thread

from future.backports import datetime

from repository.models import *
from repository.files import *
from service import publication_service
from service.image_service import get_image_hashes, check_size
from parsers.vk_parser import get_photos_by_id

logger = logging.getLogger(__name__)


def moderate_queue():
    if VkPhoto.select().where(VkPhoto.processed == False).exists():
        photos = VkPhoto.select().where(VkPhoto.processed == False).order_by(VkPhoto.rnd.asc()).first(10)
        for photo in [photo for photo in get_photos_by_id(photos)]:
            photo_url = photo.photo_1280 or photo.photo_807 or photo.photo_604
            if photo_url:
                tmp_file_path = save_by_url(photo_url)
                if not check_size(tmp_file_path):
                    logger.log(99, f'Image size is too small')
                    os.remove(tmp_file_path)
                    continue
                md5_hash = get_md5_hash(tmp_file_path)
                if File.exists_by_md5_hash(md5_hash):
                    logger.log(99, f'MD5 Hash duplication, image from url {photo_url} already exists')
                    os.remove(tmp_file_path)
                    continue
                hashes = get_image_hashes(tmp_file_path)
                if File.check_hashes(hashes):
                    logger.log(99, f'ImageHash duplication, image from url {photo_url} already exists')
                    os.remove(tmp_file_path)
                    continue
                file_path = move_file(tmp_file_path)
                with db_lock:
                    file = File(path=file_path, telegram_id='from_vk', hash_string=md5_hash,
                                image_dhash=hashes.get('dHash'), image_ahash=hashes.get('aHash'),
                                image_phash=hashes.get('pHash'), image_whash=hashes.get('wHash'), source='vk')
                    file.save()
                if not Users.select().where(Users.username == 'system').exists():
                    with db_lock:
                        Users.create(username='system', user_id=1)
                with db_lock:
                    user = Users.select().where(Users.username == 'system').first(1)
                    publication = Publication.create(user=user, item=file, creation_date=datetime.datetime.now())
                publication_service.send_to_moderation(publication)
            else:
                continue
        with db_lock:
            for vk_photo in photos:
                vk_photo.processed = True
                vk_photo.save()
        logger.log(99, 'Moderation iteration completed')
    else:
        logger.log(99, 'Nothing to moderate for VkPhoto moderation')


def moderation_loop():
    logger.log(99, 'Starting moderation loop')
    moderation_processing_time = datetime.datetime.now()
    logger.log(99, f'Next moderation iteration time {moderation_processing_time}')
    while 1:
        if datetime.datetime.now() >= moderation_processing_time:
            moderate_queue()
            moderation_processing_time = moderation_processing_time + timedelta(minutes=60)
            logger.log(99, f'Next moderation iteration time {moderation_processing_time}')
        time.sleep(10)


def start():
    moderation_thread = Thread(target=moderation_loop, name='parsing_moderation', daemon=True)
    moderation_thread.start()

import logging
import time

from future.backports import datetime
from telegram.error import BadRequest

from parsers.vk_parser import get_photos_by_id
from repository.files import *
from repository.models import *
from service import publication_service
from service.image_service import get_image_hashes, check_size

logger = logging.getLogger(__name__)


def moderate_queue():
    if VkPhoto.select().where(VkPhoto.processed == False).exists():
        references.bot.send_message(
            chat_id=cfg.moderation_chat,
            text='Выгружаю 30 публикаций из Вконтакте',
            disable_notification=True
        )
        small_images = 0
        duplicates = 0
        photos = VkPhoto.select().where(VkPhoto.processed == False).order_by(VkPhoto.rnd.asc()).first(30)
        for photo in [photo for photo in get_photos_by_id(photos)]:
            photo_url = photo.photo_1280 or photo.photo_807 or photo.photo_604
            if photo_url:
                tmp_file_path = save_by_url(photo_url)
                if not check_size(tmp_file_path):
                    logger.info(f'Image size is too small')
                    os.remove(tmp_file_path)
                    small_images += 1
                    continue
                md5_hash = get_md5_hash(tmp_file_path)
                if File.exists_by_md5_hash(md5_hash):
                    logger.info(f'MD5 Hash duplication, image from url {photo_url} already exists')
                    os.remove(tmp_file_path)
                    duplicates += 1
                    continue
                hashes = get_image_hashes(tmp_file_path)
                if File.check_hashes(hashes):
                    logger.info(f'ImageHash duplication, image from url {photo_url} already exists')
                    os.remove(tmp_file_path)
                    duplicates += 1
                    continue
                file_path = move_file(tmp_file_path)
                file = File(path=file_path, telegram_id='from_vk', hash_string=md5_hash,
                            image_dhash=hashes.get('dHash'), image_ahash=hashes.get('aHash'),
                            image_phash=hashes.get('pHash'), image_whash=hashes.get('wHash'), source='vk')
                file.save()
                if Contributor.select().where(Contributor.username == 'system').exists():
                    contributor = Contributor.select().where(Contributor.username == 'system').first(1)
                else:
                    contributor = Contributor.create(username='system', user_id=1, points=0)
                publication = Publication.create(contributor=contributor, item=file,
                                                 creation_date=datetime.datetime.now())
                publication_service.send_to_moderation(publication)
                time.sleep(3)
            else:
                continue
        for vk_photo in photos:
            vk_photo.processed = True
            vk_photo.save()
        logger.info('Moderation iteration completed')
        references.bot.send_message(
            chat_id=cfg.moderation_chat,
            text=f'Выгрузка завершена, дубликатов {duplicates}, с низким разрешением {small_images}',
            disable_notification=True
        )
    else:
        logger.info('Nothing to moderate for VkPhoto moderation')


def clean_old_messages():
    publication_for_clean = Publication.select().where(
        ((
             (Publication.creation_date <= datetime.datetime.now() - datetime.timedelta(days=1)) &
             (Publication.published == True)
         ) |
         (
             (Publication.creation_date <= datetime.datetime.now() - datetime.timedelta(days=1)) &
             (Publication.moderated == False)
         )) & (Publication.deleted == None)
    )
    if publication_for_clean.exists():
        for publication in publication_for_clean.first(100):
            try:
                logger.info(f'Trying to delete message with id {publication.message_id}')
                references.bot.delete_message(
                    chat_id=cfg.moderation_chat,
                    message_id=publication.message_id
                )
                logger.info(f'Message with id {publication.message_id} successfully cleaned')
                publication.deleted = True
            except BadRequest as e:
                logger.exception(f'Exception when deleting message with id {publication.message_id}', exc_info=True)
                publication.deleted = False
            publication.save()

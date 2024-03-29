import logging
import os

import imagehash
from PIL import Image

logger = logging.getLogger(__name__)


def get_image_hashes(file_path):
    if os.path.exists(file_path):
        image = Image.open(file_path)
        return {
            'dHash': str(imagehash.dhash(image)),
            'pHash': str(imagehash.phash(image)),
            'aHash': str(imagehash.average_hash(image)),
            'wHash': str(imagehash.whash(image))
        }
    else:
        logger.log(99, f'File with path {file_path} doesnt exists')


def check_size(file_path):
    if os.path.exists(file_path):
        try:
            image = Image.open(file_path)
            return image.width >= 300 and image.height >= 300
        except OSError as e:
            logger.error('Error when trying to open file', exc_info=True)
            return False
    else:
        logger.log(99, f'File with path {file_path} doesnt exists')

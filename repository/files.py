import hashlib
import os
import uuid

from config import config as cfg
from service import references


def save_file(file_id):
    bot = references.get_bot_reference()
    images_dir = cfg.images_dir
    while 1:
        if not os.path.exists(images_dir):
            os.mkdir(images_dir)
        image_identifier = str(uuid.uuid4())
        sub_dir = image_identifier.split('-')[:1][0]
        sub_dir_path = os.path.join(images_dir, sub_dir)
        if not os.path.exists(sub_dir_path):
            os.mkdir(sub_dir_path)
        file_name = f'{"".join(image_identifier.split("-")[1:])}.jpg'
        file_path = os.path.normpath(os.path.join(sub_dir_path, file_name))
        if not os.path.exists(file_path):
            file = open(file=file_path, mode='wb')
            image = bot.get_file(file_id=file_id)
            image.download(out=file)
            file.close()
            break
        else:
            continue
    return {'image_identifier': file_id, 'file_path': file_path}


def get_md5_hash(file_path):
    if os.path.exists(file_path):
        file = open(file=file_path, mode='rb')
        has = hashlib.md5(file.read())
        return has.hexdigest()
    else:
        raise FileNotFoundError

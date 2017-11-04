import os
import hashlib
from telegram.bot import Bot

import config
import uuid

from service import references


def save_as_tmp_file(file_id):
    bot = references.get_bot_reference()
    tmp_dir = 'temp'
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    while 1:
        tmp_file_name = f'{uuid.uuid4()}.jpg'
        tmp_file_path = os.path.normpath(os.path.join(tmp_dir, tmp_file_name))
        if not os.path.exists(tmp_file_path):
            tmp_file = open(file=tmp_file_path, mode='wb')
            bot.get_file(file_id=file_id).download(out=tmp_file)
            tmp_file.close()
            return tmp_file_path
        else:
            continue


def move_file(file_path):
    while 1:
        if not os.path.exists(config.get_images_dir()):
            os.mkdir(config.get_images_dir())
        image_identifier = str(uuid.uuid4())
        sub_dir = image_identifier.split('-')[:1][0]
        sub_dir_path = os.path.join(config.get_images_dir(), sub_dir)
        if not os.path.exists(sub_dir_path):
            os.mkdir(sub_dir_path)
        file_name = f'{"".join(image_identifier.split("-")[1:])}.jpg'
        new_file_path = os.path.normpath(os.path.join(sub_dir_path, file_name))
        if not os.path.exists(new_file_path):
            os.rename(file_path, new_file_path)
        return new_file_path


def get_md5_hash(file_path):
    if os.path.exists(file_path):
        file = open(file=file_path, mode='rb')
        has = hashlib.md5(file.read())
        return has.hexdigest()
    else:
        raise FileNotFoundError

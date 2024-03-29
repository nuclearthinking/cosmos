import hashlib
import os
import shutil
import uuid

import requests

from config import config as cfg
from service import references


def save_by_telegram(file_id):
    bot = references.get_bot_reference()
    tmp_dir = 'temp'
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    while 1:
        tmp_file_name = f'{uuid.uuid4()}.jpg'
        tmp_file_path = os.path.normpath(os.path.join(tmp_dir, tmp_file_name))
        if not os.path.exists(tmp_file_path):
            with open(file=tmp_file_path, mode='wb') as tmp_file:
                bot.get_file(file_id=file_id).download(out=tmp_file, timeout=20)
            return tmp_file_path
        else:
            continue


def save_by_url(url):
    tmp_dir = 'temp'
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    while 1:
        tmp_file_name = f'{uuid.uuid4()}.jpg'
        tmp_file_path = os.path.normpath(os.path.join(tmp_dir, tmp_file_name))
        if not os.path.exists(tmp_file_path):
            response = requests.get(url=url, stream=True)
            with open(file=tmp_file_path, mode='wb') as tmp_file:
                shutil.copyfileobj(response.raw, tmp_file)
            del response
            return tmp_file_path
        else:
            continue


def move_file(file_path):
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

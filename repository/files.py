import os

from telegram.bot import Bot

import config
import uuid

images_dir = config.IMAGES_DIR


def save_file(file_id):
    bot = Bot(token=config.TOKEN)
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
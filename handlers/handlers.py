import os

from telegram.bot import Bot
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.update import Update
from repository import files
from repository.models import File

WELCOME_MESSAGE = 'Добро пожаловать, отправь мне фотографию, я передам её нашим модераторам'
IMAGE_RECEIVED = 'Спасибо! Фотография передана модераторам канала.'
IMAGE_ALREADY_EXISTS = 'Нам уже отправляли такую фотографию.'


class Handler:
    filter = ...

    def handle(self, bot: Bot, update: Update):
        pass

    def get_filter(self):
        return self.filter

    def get_handler(self):
        return self.handle


class StartHandler(Handler):
    filter = Filters.command

    def handle(self, bot: Bot, update: Update):
        bot.send_message(chat_id=update.message.chat_id, text=WELCOME_MESSAGE)

    def get_handler(self):
        return CommandHandler('start', self.handle, filters=self.filter)


class PhotoHandler(Handler):
    filter = Filters.photo

    def handle(self, bot: Bot, update: Update):
        file_id = update.message.photo[-1].file_id
        saved_file = files.save_file(file_id)
        file_hash = files.get_md5_hash(saved_file.get('file_path'))
        if not File.select().where(File.hash_string == file_hash).peek(1):
            file = File.create(path=saved_file.get('file_path'), telegram_id=saved_file.get('image_identifier'),
                               hash_string=file_hash)
            file.save()
            bot.send_message(chat_id=update.effective_chat.id, text=IMAGE_RECEIVED)
        else:
            os.remove(saved_file.get('file_path'))
            bot.send_message(chat_id=update.effective_chat.id, text=IMAGE_ALREADY_EXISTS)

    def get_handler(self):
        return MessageHandler(filters=self.filter, callback=self.handle)

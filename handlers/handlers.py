import uuid

from telegram.bot import Bot
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.update import Update
from repository import files

WELCOME_MESSAGE = 'Добро пожаловать, отправь мне фотографию, я передам её нашим модераторам'


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
        files.save_file(file_id)

    def get_handler(self):
        return MessageHandler(filters=self.filter, callback=self.handle)

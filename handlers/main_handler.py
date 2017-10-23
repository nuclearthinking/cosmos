from telegram.bot import Bot
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.update import Update

from handlers.base_handler import Handler


class StartHandler(Handler):
    filter = Filters.all

    WELCOME_MESSAGE = 'Добро пожаловать, отправь мне фотографию, я передам её нашим модераторам'

    def handle(self, bot: Bot, update: Update):
        bot.send_message(chat_id=update.message.chat_id, text="Available commands \n"
                                                              "/status show current active users status")

    def get_handler(self):
        return CommandHandler('start', self.handle)

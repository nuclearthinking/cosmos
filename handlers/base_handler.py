from telegram.bot import Bot
from telegram.update import Update


class Handler:
    filter = ...

    def handle(self, bot: Bot, update: Update):
        pass

    def get_filter(self):
        return self.filter

    def get_handler(self):
        return self.handle

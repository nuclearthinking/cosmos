from telegram.ext.commandhandler import CommandHandler
from telegram.ext.updater import Updater

import config


def handle_start(bot, update):
    ...


start_handler = CommandHandler(command='status', callback=handle_start)


def main():
    updater = Updater(config.TOKEN)
    dp = updater.dispatcher

    dp.add_handler(start_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

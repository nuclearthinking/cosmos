from telegram.ext.updater import Updater

import config
from handlers.handlers import StartHandler, PhotoHandler


handlers = [StartHandler().get_handler(), PhotoHandler().get_handler()]


def main():
    updater = Updater(config.TOKEN)
    dp = updater.dispatcher

    [dp.add_handler(handler) for handler in handlers]
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

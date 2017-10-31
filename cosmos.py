import datetime
import logging
import os

from telegram.ext.updater import Updater

import config
from handlers.handlers import StartHandler, PhotoHandler, VoteHandler
from repository.models import User, db, File, Vote, Publication

from service import publication_service

# logging
os.mkdir('logs') if not os.path.exists('logs') else None
date = datetime.date.today()
now_time = datetime.datetime.now()
log_file_name = f"bot_{date}_{now_time.hour}-{now_time.minute}-{now_time.second}.log"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='/'.join(['logs', log_file_name]))
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

handlers = [StartHandler().get_handler(), PhotoHandler().get_handler(), VoteHandler().get_handler()]


def error(bot, update, error):
    logger.warning(f'Update {update} caused error {error}')


def main():
    db.create_tables([User, Vote, File, Publication], safe=True)

    updater = Updater(config.get_token())
    dp = updater.dispatcher

    [dp.add_handler(handler) for handler in handlers]
    dp.add_error_handler(error)
    updater.start_polling()
    publication_service.start_publications()
    updater.idle()


if __name__ == '__main__':
    main()
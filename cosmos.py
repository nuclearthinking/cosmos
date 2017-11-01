import logging

from telegram.ext.updater import Updater

from config import config as cfg
from handlers.handlers import *
from repository.models import *
from service import publication_service, references

# logging
os.mkdir('logs') if not os.path.exists('logs') else None
date = datetime.date.today()
now_time = datetime.datetime.now()
log_file_name = f"bot_{date}_{now_time.hour}-{now_time.minute}-{now_time.second}.log"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='/'.join(['logs', log_file_name]))
logger = logging.getLogger(__name__)

handlers = [StartHandler().get_handler(), PhotoHandler().get_handler(), VoteHandler().get_handler()]


def error(bot, update, error):
    logger.warning(f'Update {update} caused error {error}')


def main():
    db.create_tables([User, File, Publication, Vote, ParsingSource, ParsedItem], safe=True)

    updater = Updater(cfg.token)
    dp = updater.dispatcher
    references.set_bot_reference(updater.bot)
    [dp.add_handler(handler) for handler in handlers]
    dp.add_error_handler(error)
    updater.start_polling()
    publication_service.start_publications()
    updater.idle()


if __name__ == '__main__':
    main()

import logging

from telegram.ext.updater import Updater

from config import config as cfg
from handlers.handlers import *
from parsers import vk_parser
from repository.models import *
from service import publication_service, references, moderation

# logging
os.mkdir('logs') if not os.path.exists('logs') else None
date = datetime.date.today()
now_time = datetime.datetime.now()
log_file_name = f"bot_{date}_{now_time.hour}-{now_time.minute}-{now_time.second}.log"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='/'.join(['logs', log_file_name]), level=99)
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.isEnabledFor(99)

handlers = [StartHandler().get_handler(),
            PhotoHandler().get_handler(),
            VoteHandler().get_handler(),
            StartParsingHandler().get_handler()]


def error(bot, update, error):
    logger.log(99, f'Update {update} caused error {error}')


def main():
    db.create_tables([User, File, Publication, Vote, ParsingSource, VkPhoto], safe=True)
    load_parsing_sources()
    updater = Updater(cfg.token)
    dp = updater.dispatcher
    references.set_bot_reference(updater.bot)
    [dp.add_handler(handler) for handler in handlers]
    dp.add_error_handler(error)
    updater.start_polling()
    publication_service.start_publications()
    moderation.start()
    updater.idle()


def load_parsing_sources():
    groups = cfg.vk_groups
    for group in groups:
        if not ParsingSource.select().where(ParsingSource.domain == group).exists():
            ParsingSource.create(domain=group).save()


if __name__ == '__main__':
    main()

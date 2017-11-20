from logging import INFO

from telegram.ext.updater import Updater

from handlers.handlers import *
from repository.models import *
from service import publication_service, references
from service.schedule_service import Schedule

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=INFO
)
logger = logging.getLogger(__name__)

handlers = [
    StartHandler().get_handler(),
    PhotoHandler().get_handler(),
    VoteHandler().get_handler(),
    StartParsingHandler().get_handler(),
    QueueLength().get_handler()
]


def error(bot, update, error):
    logger.log(99, f'Update {update} caused error {error}')


def main():
    db.create_tables([File, Publication, Vote, ParsingSource, VkPhoto, Contributor, Moderator], safe=True)
    load_parsing_sources()
    updater = Updater(cfg.token)
    dp = updater.dispatcher
    references.set_bot_reference(updater.bot)
    [dp.add_handler(handler) for handler in handlers]
    dp.add_error_handler(error)
    updater.start_polling()
    publication_service.prepare_publications()
    schedule = Schedule()
    schedule.start()
    updater.idle()


def load_parsing_sources():
    groups = cfg.vk_groups
    for group in groups:
        if not ParsingSource.select().where(ParsingSource.domain == group).exists():
            ParsingSource.create(domain=group).save()


if __name__ == '__main__':
    main()

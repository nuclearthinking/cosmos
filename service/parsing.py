from threading import Thread

from config import config as cfg
from parsers import vk_parser
from repository.models import ParsingSource, VkPhoto, db_lock
from service import references


class Parser(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, 'vk_parser', args, kwargs, daemon=daemon)

    def run(self):
        _start_parsing()


def _start_parsing():
    with db_lock:
        parsing_sources = ParsingSource.select()
        initial_rows = VkPhoto.select().count()
    for source in parsing_sources:
        vk_parser.parse_group(source)
    with db_lock:
        result_rows = VkPhoto.select().count()
    diff_rows = result_rows - initial_rows
    references.bot.send_message(
        chat_id=cfg.moderation_chat,
        text=f'Парсинг завершен, получено {diff_rows} фотографий'
    )


def start():
    parser = Parser()
    references.set_parser_reference(parser)
    parser.start()

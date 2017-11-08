from telegram.bot import Bot

from service.parsing import Parser

bot: Bot = ...
parser: Parser = ...


def get_bot_reference() -> Bot:
    global bot
    return bot


def set_bot_reference(bot_reference: Bot):
    global bot
    bot = bot_reference


def set_parser_reference(parser_reference: Parser):
    global parser
    parser = parser_reference


def get_parser_reference():
    global parser
    return parser

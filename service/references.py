from telegram.bot import Bot

bot: Bot = ...


def get_bot_reference() -> Bot:
    global bot
    return bot


def set_bot_reference(bot_reference: Bot):
    global bot
    bot = bot_reference

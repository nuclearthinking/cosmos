import datetime
import json
import logging
import threading
from datetime import timedelta
from typing import List

import time
from telegram.bot import Bot
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

import config
from repository.models import Publication, Vote

on_moderation: List[Publication] = []
moderated: List[Publication] = []
logger = logging.getLogger(__name__)


def send_to_moderation(publication: Publication):
    bot = Bot(token=config.TOKEN)
    publication_id = publication.id
    file = open(file=publication.item.path, mode='rb')

    def get_star_button(starts):
        text = '⭐️' * starts
        callback = {
            'publication_id': publication_id,
            'points': starts
        }
        return InlineKeyboardButton(text=text, callback_data=json.dumps(callback))

    buttons = [
        [get_star_button(5), get_star_button(4)],
        [get_star_button(3), get_star_button(2), get_star_button(1)]
    ]
    markup = InlineKeyboardMarkup(buttons)
    message = bot.send_photo(
        chat_id=config.MODERATION_CHAT_ID,
        photo=file,
        reply_markup=markup
    )
    publication.message_id = message.message_id
    publication.save()
    on_moderation.append(publication)


def process_moderation(interval):
    while True:
        if on_moderation:
            try:
                publication = on_moderation.pop(0)
                votes = Vote.select().where(Vote.publication_id == publication.id).first(100)
                if datetime.datetime.now() > (publication.creation_date + timedelta(hours=config.VOTE_TIME_LIMIT)) and len(votes) > 0:
                    score = 0.0
                    for x in [vote.points for vote in votes]:
                        score = score + x
                    score = round(score / len(votes), 2)
                    publication.score = score
                    publication.update()
                    if score > 3:
                        moderated.append(publication)
                    else:
                        publication.published = False
                        publication.update()
                else:
                    on_moderation.append(publication)
            except Exception as e:
                logger.exception("Exception occured while processing on moderation queue")
        else:
            pass
        time.sleep(interval)


def publication_loop(interval):
    last_publication_time = datetime.datetime.now()
    while 1:
        if datetime.datetime.now() > last_publication_time + timedelta(minutes=config.PUBLICATION_INTERVAL):
            last_publication_time = datetime.datetime.now()
            process_publication()
        time.sleep(interval)


def process_publication():
    if moderated:
        bot = Bot(token=config.TOKEN)
        publication = moderated.pop(0)
        bot.send_photo(
            chat_id=config.PUBLICATION_CHANNEL,
            photo=open(
                file=publication.item.path,
                mode='rb'
            )
        )
        publication.published = True
        publication.publishing_date = datetime.datetime.now()
        publication.update()


def start_publications():
    if Publication.select().where(Publication.published == None).exists():
        for publication in Publication.select().where(Publication.published == None).first(999):
            on_moderation.append(publication)
    moderation_thread = threading.Thread(target=process_moderation, args=(15,))
    moderation_thread.setName("moderation")
    moderation_thread.daemon = True
    moderation_thread.start()

    publication_thread = threading.Thread(target=publication_loop, args=(15,))
    publication_thread.setName("publication")
    publication_thread.daemon = True
    publication_thread.start()

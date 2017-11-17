import datetime
import json
import logging
import random
from datetime import timedelta
from typing import List

from telegram.error import BadRequest
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from config import config as cfg
from repository.models import Publication, Vote
from service import references

on_moderation: List[Publication] = []
moderated: List[Publication] = []
logger = logging.getLogger(__name__)


def send_to_moderation(publication: Publication):
    bot = references.get_bot_reference()
    publication_id = publication.id
    file = open(file=publication.item.path, mode='rb')
    markup = get_reply_markup(publication_id)
    message = bot.send_photo(
        chat_id=cfg.moderation_chat,
        photo=file,
        reply_markup=markup,
        timeout=30,
        disable_notification=True
    )
    publication.message_id = message.message_id
    publication.save()
    on_moderation.append(publication)


def get_reply_markup(publication_id):
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
    return InlineKeyboardMarkup(buttons)


def process_moderation():
    if on_moderation:
        try:
            publication = on_moderation.pop(0)
            if publication.message_id is None:
                logger.error('Publication doesnt hav message_id, we cant moderate it, skipping')
                pass
            else:
                if Vote.select().where(Vote.publication_id == publication.id).exists():
                    votes = Vote.select().where(Vote.publication_id == publication.id).first(100)
                else:
                    votes = []
                logger.info(f'Processing publication with id {publication.id}')
                moderation_end_time = publication.creation_date + timedelta(minutes=cfg.moderation_timeout)
                if datetime.datetime.now() > moderation_end_time and len(
                        votes) >= cfg.votes_to_finish and publication.published is None:
                    score = 0.0
                    for x in [vote.points for vote in votes]:
                        score = score + x
                    score = round(score / len(votes), 2)
                    publication.score = score
                    publication.save()
                    bot = references.get_bot_reference()
                    try:
                        bot.edit_message_reply_markup(
                            chat_id=cfg.moderation_chat,
                            message_id=publication.message_id,
                            reply_markup=None,
                            timeout=20
                        )
                    except BadRequest as e:
                        logger.exception(f'Exception occurred while editing message with id {publication.message_id}')
                    message_text = f'Проголосовало: {len(votes)}\nСредняя оценка: {score}'
                    if score >= cfg.points_to_publish:
                        publication.moderated = True
                        publication.save()
                        moderated.append(publication)
                    else:
                        publication.moderated = False
                        publication.save()
                        message_text += '\nФотография не прошла модерацию'
                    try:
                        bot.edit_message_caption(
                            chat_id=cfg.moderation_chat,
                            message_id=publication.message_id,
                            caption=message_text,
                            timeout=20
                        )
                    except BadRequest as e:
                        logger.info(f'Error occurred while editing message with id {publication.message_id}')

                else:
                    on_moderation.append(publication)
        except Exception as e:
            logger.exception(f"Exception occurred while processing publication with id {publication.id}")
    else:
        pass


def process_publication():
    logger.info('Starting process publication')
    if moderated:
        bot = references.get_bot_reference()
        publication = moderated.pop(random.randrange(len(moderated)))
        logger.info(f'Publishing publication with id {publication.id}')
        try:
            bot.send_photo(
                chat_id=cfg.publication_channel,
                photo=open(
                    file=publication.item.path,
                    mode='rb'
                )
            )
            try:
                bot.edit_message_caption(
                    chat_id=cfg.moderation_chat,
                    message_id=publication.message_id,
                    caption='Фотография опубликована',
                    timeout=20
                )
            except BadRequest as e:
                logger.exception(f'Message already changed')
            publication.published = True
            publication.publishing_date = datetime.datetime.now()
            publication.save()
            logger.info(f'Publishing  publication with id {publication.id} successfully done')
        except Exception as e:
            logger.exception(f'Exception occurred while publishing publication with id {publication.id}')


def prepare_publications():
    if Publication.select().where(Publication.moderated == None).exists():
        logger.info('Fetching on_moderation publications from database')
        on_moderation_publications = Publication.select().where(Publication.moderated == None).first(999)
        for publication in on_moderation_publications:
            on_moderation.append(publication)
        logger.info(f'Fetched {len(on_moderation_publications)} items')
    else:
        logger.warning('Doesnt exist\'s publications in moderation queue')
    if Publication.select().where((Publication.moderated == True) & (Publication.published == None)):
        logger.info('Fetching moderated publications from database')
        moderated_publications = Publication.select().where(
            (Publication.moderated == True) & (Publication.published == None)).first(999)
        for publication in moderated_publications:
            moderated.append(publication)
        logger.info(f'Fetched {len(moderated_publications)} items')
    else:
        logger.warning('Doesnt exist moderated publications')

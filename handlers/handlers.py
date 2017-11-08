import datetime
import json
import logging
import os

from telegram.bot import Bot
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.update import Update

from config import config as cfg
from repository import files
from repository.models import File, Publication, Vote, Contributor, Moderator
from service import image_service
from service import publication_service, parsing

WELCOME_MESSAGE = 'Добро пожаловать, отправь мне фотографию, я передам её нашим модераторам'
IMAGE_RECEIVED = 'Спасибо! Фотография передана модераторам канала.'
IMAGE_ALREADY_EXISTS = 'Нам уже отправляли такую фотографию.'
IMAGE_TOO_SMALL = 'Размер изображения слишком маленький'

logger = logging.getLogger(__name__)


class Handler:
    filter = ...

    def handle(self, bot: Bot, update: Update):
        pass

    def get_filter(self):
        return self.filter

    def get_handler(self):
        return self.handle


class StartHandler(Handler):
    filter = Filters.command & Filters.private

    def handle(self, bot: Bot, update: Update):
        bot.send_message(chat_id=update.message.chat_id, text=WELCOME_MESSAGE)

    def get_handler(self):
        return CommandHandler('start', self.handle, filters=self.filter)


class PhotoHandler(Handler):
    filter = Filters.photo & Filters.private

    def handle(self, bot: Bot, update: Update):
        try:
            contributor = ...
            if not Contributor.select().where(Contributor.user_id == update.effective_user.id).exists():
                contributor = Contributor.create(user_id=update.effective_user.id,
                                                 username=update.effective_user.username or update.effective_user.first_name,
                                                 points=0)
            else:
                contributor = Contributor.select().where(Contributor.user_id == update.effective_user.id).peek(1)
            file_id = update.message.photo[-1].file_id
            tmp_file_path = files.save_by_telegram(file_id)
            file_hash = files.get_md5_hash(tmp_file_path)
            if not File.select().where(File.hash_string == file_hash).exists():
                if not image_service.check_size(tmp_file_path):
                    logger.log(99, f'Image too small')
                    bot.send_message(chat_id=update.effective_chat.id, text=IMAGE_TOO_SMALL)
                    os.remove(tmp_file_path)
                else:
                    image_hashes = image_service.get_image_hashes(tmp_file_path)
                    if not File.select().where((File.image_whash == image_hashes.get('wHash')) |
                                                       (File.image_phash == image_hashes.get('pHash')) |
                                                       (File.image_dhash == image_hashes.get('dHash')) |
                                                       (File.image_ahash == image_hashes.get('aHash'))).exists():
                        file_path = files.move_file(tmp_file_path)
                        file = File.create(path=file_path, telegram_id=file_id, hash_string=file_hash,
                                           image_dhash=image_hashes.get('dHash'), image_ahash=image_hashes.get('aHash'),
                                           image_phash=image_hashes.get('pHash'), image_whash=image_hashes.get('wHash'),
                                           source='tg')
                        publication = Publication(contributor=contributor, item=file,
                                                  creation_date=datetime.datetime.now())
                        publication.save()
                        bot.send_message(chat_id=update.effective_chat.id, text=IMAGE_RECEIVED)
                        publication_service.send_to_moderation(publication)
                    else:
                        os.remove(tmp_file_path)
                        bot.send_message(chat_id=update.effective_chat.id, text=IMAGE_ALREADY_EXISTS)
            else:
                os.remove(tmp_file_path)
                bot.send_message(chat_id=update.effective_chat.id, text=IMAGE_ALREADY_EXISTS)
        except Exception as e:
            logger.log(99, 'Exception occured during handling photo', e)

    def get_handler(self):
        return MessageHandler(filters=self.filter, callback=self.handle)


class VoteHandler(Handler):
    filter = Filters.chat(chat_id=cfg.moderation_chat)

    def handle(self, bot: Bot, update: Update, user_data, chat_data):
        data = json.loads(update.callback_query.data)
        moderator = ...
        if Moderator.select().where(Moderator.user_id == update.callback_query.from_user.id).exists():
            moderator = Moderator.select().where(Moderator.user_id == update.callback_query.from_user.id).peek(1)
        else:
            moderator = Moderator(user_id=update.callback_query.from_user.id,
                                  username=update.callback_query.from_user.username or update.callback_query.from_user.first_name)
            moderator.save()
        if Vote.select().where(Vote.moderator == moderator, Vote.publication_id == data.get('publication_id'),
                               Vote.points > 0).exists():
            bot.answer_callback_query(
                callback_query_id=update.callback_query.id,
                text='Вы уже голосовали',
                show_alert=False
            )
        else:
            vote = Vote(
                publication_id=data.get('publication_id'),
                moderator=moderator,
                date=datetime.datetime.now(),
                points=data.get('points'),
            )
            vote.save()
            bot.answer_callback_query(
                callback_query_id=update.callback_query.id,
                text='Ваш голос принят',
                show_alert=False
            )

    def get_handler(self):
        return CallbackQueryHandler(callback=self.handle, pass_chat_data=True, pass_groupdict=True, pass_user_data=True)


class StartParsingHandler(Handler):
    filter = Filters.chat(chat_id=cfg.moderation_chat) & Filters.command & Filters.user(username='nuclearthinking')

    def handle(self, bot: Bot, update: Update):
        parsing.start()
        bot.send_message(
            chat_id=cfg.moderation_chat,
            text='Запущен парсинг групп в контакте'
        )

    def get_handler(self):
        return CommandHandler('parse', self.handle, filters=self.filter)

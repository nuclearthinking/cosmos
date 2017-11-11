import datetime
import logging

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_ADDED, EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from config import config as cfg
from service import moderation, publication_service
from utils import utils

logger = logging.getLogger(__name__)


class Schedule:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(Schedule.listener, mask=EVENT_JOB_ERROR | EVENT_JOB_ADDED | EVENT_JOB_EXECUTED)
        self.parsing_moderation_job = self.scheduler.add_job(
            func=moderation.moderate_queue,
            trigger=CronTrigger(
                start_date=utils.round_publication_date(datetime.datetime.now()),
                second=0,
                minute=0,
                hour='*/3'
            ),
            id='parsing_moderation_job',
            name='VK Parsing Moderation',
            max_instances=1
        )
        self.publication_moderation_job = self.scheduler.add_job(
            func=publication_service.process_moderation,
            trigger=IntervalTrigger(seconds=5, start_date=datetime.datetime.now()),
            id='publication_moderation_job',
            name='Publication Moderation Job',
            max_instances=1
        )
        self.publication_job = self.scheduler.add_job(
            func=publication_service.process_publication,
            trigger=IntervalTrigger(
                start_date=utils.round_publication_date(datetime.datetime.now()),
                minutes=cfg.publication_interval
            ),
            id='publications_job',
            name='Publications Job',
            max_instances=1
        )
        self.clean_job = self.scheduler.add_job(
            func=moderation.clean_old_messages,
            trigger=IntervalTrigger(
                start_date=datetime.datetime.now(),
                minutes=5,
            ),
            name='Cleanup Messages Job'
        )

    def start(self):
        self.scheduler.start()

    @staticmethod
    def listener(event):
        if event.code == EVENT_JOB_ERROR:
            logger.exception('Exception while executing job')
        elif event.code == EVENT_JOB_ADDED:
            logger.info(f'Added job with id {event.job_id}')
        elif event.code == EVENT_JOB_EXECUTED:
            logger.info(f'Job with id {event.job_id} successfully executed')

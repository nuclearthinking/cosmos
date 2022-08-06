"""
https://api.vk.com/api.php?oauth=1&method=wall.get&v=5.69&filter=all&domain=awe.some&count=5&access_token=6c5f17a96c5f17a96c5f17a9ea6c07cb1066c5f6c5f17a935a7db63319cf8820c2e73b2
"""
import json
import logging
import random
import time
from typing import List

from requests import get

from config import config as cfg
from parsers.vk_entity import Response, GetPhotosById
from repository.models import VkPhoto, ParsingSource, db_lock

VK_API_URL = "https://api.vk.com/api.php"

logger = logging.getLogger(__name__)


def wall_get_params(count, offset, group_domain):
    if count <= 100:
        return {
            'v': 5.69,
            'oauth': 1,
            'method': 'wall.get',
            'filter': 'all',
            'domain': group_domain,
            'count': count,
            'offset': offset,
            'access_token': cfg.vk_token
        }
    else:
        raise ValueError('Count cannot be grater than 100')


def photos_get_params(photos: List[VkPhoto]):
    return {
        'v': 5.69,
        'oauth': 1,
        'method': 'photos.getById',
        'photos': ','.join([f'{p.owner_id}_{p.photo_id}' for p in photos]),
        'access_token': cfg.vk_token
    }


def get_photos_by_id(photos: List[VkPhoto]):
    params = photos_get_params(photos)
    r = get(url=VK_API_URL, params=params)
    r_dict = json.loads(r.content.decode())
    return GetPhotosById(**r_dict).response


def get_wall_posts(offset, count, group_domain):
    params = wall_get_params(count, offset, group_domain)
    r = get(url=VK_API_URL, params=params)
    response_dict = json.loads(r.content.decode())
    return Response(**response_dict.get('response')).items


def get_posts_count(group_domain):
    params = wall_get_params(1, 1, group_domain)
    r = get(url=VK_API_URL, params=params)
    response_dict = json.loads(r.content.decode())
    return Response(**response_dict.get('response')).count


def parse_group(group: ParsingSource):
    logger.log(99, f'Starting parsing group {group.domain}')
    posts_count = get_posts_count(group.domain)
    if group.parsed_posts < posts_count:
        insert_array = []
        start_post = group.parsed_posts
        end_post = group.parsed_posts
        while end_post < posts_count:
            logger.log(99, f'Fetching items from {start_post} to {start_post+100}')
            if items := get_wall_posts(start_post, 100, group.domain):
                for item in items:
                    if item.attachments:
                        for attachment in item.attachments:
                            if attachment.type == 'photo':
                                photo = attachment.photo
                                insert_array.append({'photo_id': photo.id, 'owner_id': photo.owner_id,
                                                     'rnd': random.randint(1, 100000)})
                if insert_array:
                    VkPhoto.insert_many(insert_array).execute()
                insert_array.clear()
                group.parsed_posts = start_post + len(items)
                group.save()
                start_post += len(items)
                end_post += len(items)
                logger.log(99, f'Successfully fetched {len(items)}')
            else:
                logger.log(99, 'No new items ')
                break
            time.sleep(3)
        logger.log(99, f'Parsing source {group.domain} successfully completed')
    else:
        logger.log(99, f'Nothing new to parse from {group.domain}')

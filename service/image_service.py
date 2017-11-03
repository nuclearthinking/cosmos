import logging
import os

from PIL import Image
from imagehash import dhash, hex_to_hash, phash, average_hash, whash

from repository.models import File

logger = logging.getLogger(__name__)


def get_image_hashes(file_path):
    if os.path.exists(file_path):
        image = Image.open(file_path)
        return {
            'dhash': str(dhash(image, hash_size=16)),
            'phash': str(phash(image, hash_size=16)),
            'ahash': str(average_hash(image, hash_size=16)),
            'whash': str(whash(image, hash_size=16))
        }
    else:
        logger.error(f'File with path {file_path} doesnt exists')


def find_similar_images(initial_file):
    image_hash = initial_file.image_hash
    initial_image_hash = hex_to_hash(image_hash)
    for file in File.select():
        db_file_hash = hex_to_hash(file.image_hash)

        if initial_file.id != file.id:
            if hex_to_hash(initial_file.image_dhash,hash_size=16) == hex_to_hash(file.image_dhash, hash_size=16):
                print('Match found')
                print_file_info(file, initial_file, 'dHash')
                Image.open(file.path).show()
            elif hex_to_hash(initial_file.image_ahash, hash_size=16) == hex_to_hash(file.image_ahash, hash_size=16):
                print('Match found')
                print_file_info(file, initial_file, 'aHash')
                Image.open(file.path).show()
            elif hex_to_hash(initial_file.image_whash, hash_size=16) == hex_to_hash(file.image_whash, hash_size=16):
                print('Match found')
                print_file_info(file, initial_file, 'wHash')
                Image.open(file.path).show()
            elif hex_to_hash(initial_file.image_phash, hash_size=16) == hex_to_hash(file.image_phash, hash_size=16):
                print('Match found')
                print_file_info(file, initial_file, 'pHash')
                Image.open(file.path).show()
            else:
                dhash_diff = hex_to_hash(initial_file.image_dhash, hash_size=16) - hex_to_hash(file.image_dhash, hash_size=16)
                ahash_diff = hex_to_hash(initial_file.image_ahash, hash_size=16) - hex_to_hash(file.image_ahash, hash_size=16)
                whash_diff = hex_to_hash(initial_file.image_whash, hash_size=16) - hex_to_hash(file.image_whash, hash_size=16)
                phash_dif = hex_to_hash(initial_file.image_phash, hash_size=16) - hex_to_hash(file.image_phash, hash_size=16)
                if dhash_diff <= 10:
                    print(f'dhash_diff {dhash_diff} < 10')
                    print(f'initial_file path {initial_file.path}')
                    print(f'file pat {file.path}')
                    # Image.open(file.path).show()
                    # Image.open(initial_file.path).show()
                elif ahash_diff <= 10:
                    print(f'ahash_diff {ahash_diff} < 10')
                    print(f'initial_file path {initial_file.path}')
                    print(f'file pat {file.path}')
                    # Image.open(file.path).show()
                    # Image.open(initial_file.path).show()
                elif whash_diff <= 10:
                    print(f'whash_diff {whash_diff} < 10')
                    print(f'initial_file path {initial_file.path}')
                    print(f'file pat {file.path}')
                    # Image.open(file.path).show()
                    # Image.open(initial_file.path).show()
                elif phash_dif <= 10:
                    print(f'phash_dif {phash_dif} < 10')
                    print(f'initial_file path {initial_file.path}')
                    print(f'file pat {file.path}')
                    # Image.open(file.path).show()
                    # Image.open(initial_file.path).show()


def print_file_info(file, initial_file, hash_type):
    print(f'Hash type {hash_type}')
    print(f"path {file.path}")
    print(f'initial_file path {initial_file.path}')
    print(f"id {file.id}")
    print(f'hash_string {file.hash_string}')
    print(f'image_hash {file.image_hash}')
    print('*' * 10)

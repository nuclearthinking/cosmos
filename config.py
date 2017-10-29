from ruamel.yaml.main import YAML

config = YAML().load(open('config.yml').read())

TOKEN = config.get('token')
IMAGES_DIR = config.get('images_dir')
MODERATION_CHAT_ID = config.get('moderators_channel')
PUBLICATION_CHANNEL = config.get('publications_channel')
PUBLICATION_INTERVAL = config.get('publication_interval')
VOTE_TIME_LIMIT = config.get('moderation_timeout')
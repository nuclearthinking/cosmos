from ruamel.yaml.main import YAML


def get_setting(setting_name):
    return YAML().load(open('config.yml').read()).get(setting_name)


def get_token():
    return get_setting('token')


def get_images_dir():
    return get_setting('images_dir')


def get_moderation_chat():
    return get_setting('moderators_channel')


def get_publication_channel():
    return get_setting('publications_channel')


def get_publication_interval():
    return get_setting('publication_interval')


def get_moderation_time_limit():
    return get_setting('moderation_timeout')

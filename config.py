from ruamel.yaml.main import YAML


def get_setting(setting_name):
    return YAML().load(open('config.yml').read()).get(setting_name)


class Configuration:
    @property
    def token(self):
        return get_setting('token')

    @property
    def images_dir(self):
        return get_setting('images_dir')

    @property
    def moderation_timeout(self):
        return get_setting('moderation_timeout')

    @property
    def vk_token(self):
        return get_setting('vk_token')

    @property
    def vk_groups(self):
        return get_setting('vk_groups')

    @property
    def publication_interval(self):
        return get_setting('publication_interval')

    @property
    def publication_channel(self):
        return get_setting('publications_channel')

    @property
    def moderation_chat(self):
        return get_setting('moderators_channel')


config = Configuration()

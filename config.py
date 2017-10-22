from ruamel.yaml.main import YAML

config = YAML().load(open('config.yml').read())

TOKEN = config.get('token')

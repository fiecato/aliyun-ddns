import configparser
import os


# pylint: disable=C0103
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "domain.cfg")
config.read(config_path)


def get(section, key):
    try:
        return os.environ[section + '_' + key]
    except KeyError:
        return config.get(section, key)


def get_all(section):
    lists = []
    for items in config.items(section):
        lists.append(get(section, items[0]))
    return lists

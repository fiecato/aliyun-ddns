import logging
import common.config as cfg
from logging.handlers import RotatingFileHandler


__level__ = cfg.get('logging', 'level')
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',  # noqa: E501
    datefmt='%Y-%m-%d %H:%M:%S %z')


__root_logger__ = logging.getLogger()
__formatter__ = logging.Formatter(
    '[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %z')


def add_rhandler():
    handler = RotatingFileHandler(
        filename=cfg.get('db', 'path') + '/ddns.log',
        maxBytes=1 * 1024 * 1024 * 1024,
        backupCount=3)
    handler.setLevel(__level__)
    handler.setFormatter(__formatter__)
    return handler


def get_logger(name):
    logger = __root_logger__.getChild(name)
    logger.setLevel(__level__)
    logger.addHandler(add_rhandler())
    return logger
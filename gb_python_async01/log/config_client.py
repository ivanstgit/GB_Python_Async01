# создаём формировщик логов (formatter):
import logging
import os
import sys

LOGGER_NAME = 'client'


def init_logger(debug=False, testing=False):
    if debug or testing:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.ERROR)

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'client', 'client.log')
    file_handler = logging.FileHandler(file_path, encoding='utf-8')
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(LOGGER_NAME)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.setLevel(log_level)

    return logger


def get_logger():
    logger = logging.getLogger(LOGGER_NAME)
    if len(logger.handlers):
        return logger
    return None


# отладка
if __name__ == '__main__':
    init_logger(True, True)
    logger = get_logger()
    if logger:
        logger.critical('Критическая ошибка')
        logger.error('Ошибка')
        logger.debug('Отладочная информация')
        logger.info('Информационное сообщение')

"""Конфигурация логирования"""
import logging
import os
import sys


class ClientLogger:
    logger_name = "client"

    def __init__(self, file_path, debug=False, testing=False):
        if debug or testing:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO

        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(filename)s %(message)s"
        )

        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.ERROR)

        file_path = file_path
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)

        logger = logging.getLogger(self.logger_name)
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
        logger.setLevel(log_level)

        self._logger = logger

    @property
    def logger(self) -> logging.Logger:
        return self._logger


# def get_logger():
#     logger = logging.getLogger(LOGGER_NAME)
#     if len(logger.handlers):
#         return logger
#     return None


# отладка
if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.log")
    logger = ClientLogger(file_path, debug=True, testing=True).logger
    if logger:
        logger.critical("Критическая ошибка")
        logger.error("Ошибка")
        logger.debug("Отладочная информация")
        logger.info("Информационное сообщение")

from functools import wraps
import inspect
import os
import traceback


class Log:
    """Logging function calls"""

    def __init__(self, logger):
        self.logger = logger

    def __call__(self, func):
        @wraps(func)
        def log(*args, **kwargs):
            s1 = traceback.format_stack()
            func_code_filename = func.__code__.co_filename
            call_stack_prev = inspect.stack()[1]

            self.logger.debug(
                f'Функция {func.__name__} модуля {os.path.split(func_code_filename)[1]}'
                f' вызвана c параметрами {args}, {kwargs}'
                f' из модуля {os.path.split(call_stack_prev.filename)[1]}, функции {call_stack_prev.function}',
                stacklevel=2)

            result = func(*args, **kwargs)
            return result
        return log

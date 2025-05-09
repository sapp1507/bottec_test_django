import functools
import os
from copy import deepcopy

from loguru import logger

from core.settings import BASE_DIR

LOGS_DIR = os.path.join(BASE_DIR, 'logs')

if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)

ROTATION = '1 month'
RETENTION = '3 month'
command_logger_format = '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}'

class Logging:
    _logger = None

    @staticmethod
    def set_logger(logger_,
                   filename,
                   rotation=ROTATION,
                   retention=RETENTION,
                   compression=True,
                   serializer=False,
                   format=None
                   ) -> logger:

        logger_.add(
            os.path.join(LOGS_DIR, f'{filename}.log'),
            rotation=rotation,
            retention=retention,
            compression='zip' if compression else None,
            format=command_logger_format if format is None else format
        )
        return logger_

logger.remove()
logging_bot = Logging.set_logger(deepcopy(logger), 'bot')
logging_django = Logging.set_logger(deepcopy(logger), 'django')

# def log_exceptions(log):
#     def decorator(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             try:
#                 ic('wrapper')
#                 result = func(*args, **kwargs)
#                 return result
#             except Exception as e:
#                 log.error(
#                     f'Ошибка в {func.__module__}.{func.__name__}: {e}'
#                 )
#         return wrapper
#     return decorator
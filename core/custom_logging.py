import logging
import sys
from pprint import pformat

from loguru import logger

class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        0: 'NOTSET',
    }

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id='app')
        log.opt(
            depth=depth,
            exception=record.exc_info
        ).log(level, record.getMessage())

def format_record(record: dict) -> str:
    format_string = ("{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                     "{level: <8} | "
                     "{name}:{function}:{line} - "
                     "{extra[ip]} {message}")
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\\n[EXTRA] {extra[payload]}"

    format_string += "{exception}\\n"
    return format_string

logger.remove()
logger.add(sys.stdout, level="DEBUG", backtrace=True)
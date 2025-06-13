import logging
import datetime

import json_log_formatter
from typing import Any


class APILogFormatter(json_log_formatter.JSONFormatter):
    def json_record(
        self,
        message: str,
        extra: dict[str, str | int | float],
        record: logging.LogRecord,
    ) -> dict[str, Any]:
        return dict(
            level=record.levelname,
            time=datetime.datetime.fromtimestamp(record.created),
            message=message,
            extra=extra,
        )


class VerboseJSONFormatter(json_log_formatter.VerboseJSONFormatter):
    """
    Wrapper to make logs uniform / easy to search
    """

    def json_record(
        self,
        message: str,
        extra: dict[str, str | int | float],
        record: logging.LogRecord,
    ):
        log_item = super().json_record(message, extra, record)
        log_item["level"] = log_item.pop("levelname")

        return log_item


"""
Wrappers to make logger name typo-proof
"""


def log_info(msg, *args, **kwargs):
    logger = logging.getLogger("bia.search.api")
    return logger.info(msg, *args, **kwargs)


def log_access(msg, *args, **kwargs):
    logger = logging.getLogger("bia.search.access")
    return logger.info(msg, *args, **kwargs)


def log_error(msg, *args, **kwargs):
    logger = logging.getLogger("bia.search.api")
    return logger.error(msg, *args, **kwargs)

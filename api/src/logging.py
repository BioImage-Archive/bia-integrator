import logging
import datetime

import json_log_formatter


class APILogFormatter(json_log_formatter.JSONFormatter):
    def json_record(
        self,
        message: str,
        extra: dict[str, str | int | float],
        record: logging.LogRecord,
    ) -> dict[str, str | int | float]:
        return dict(
            level=record.levelname,
            time=datetime.datetime.fromtimestamp(record.created),
            message=message,
            extra=extra,
        )


class AccesslogFormatter(json_log_formatter.JSONFormatter):
    def json_record(
        self,
        message: str,
        extra: dict[str, str | int | float],
        record: logging.LogRecord,
    ) -> dict[str, str | int | float]:
        return dict(
            level=record.levelname,
            response_time_ms=int(record.msecs),
            time=datetime.datetime.fromtimestamp(record.created),
            source=record.args[0],
            verb=record.args[1],
            path=record.args[2],
            status=record.args[4],
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
Wrappers to make sure we always do logs right
    - never use a global logger to avoid locks
    - don't DI the logger to avoid messyness
Name tweaked to avoid mixup with logging functions
"""


def log_info(msg, *args, **kwargs):
    logger = logging.getLogger("bia.api")
    return logger.info(msg, *args, **kwargs)


def log_error(msg, *args, **kwargs):
    logger = logging.getLogger("bia.api")
    return logger.error(msg, *args, **kwargs)

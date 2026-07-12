"""
logger.py
Central logging utility.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import config


class BotLogger:
    _logger = None

    @classmethod
    def get_logger(cls):
        if cls._logger:
            return cls._logger

        Path(config.LOG_DIR).mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("indodax_bot")
        logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))

        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )

        console = logging.StreamHandler()
        console.setFormatter(fmt)

        logfile = Path(config.LOG_DIR) / "bot.log"
        file_handler = RotatingFileHandler(
            logfile,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(fmt)

        logger.addHandler(console)
        logger.addHandler(file_handler)

        cls._logger = logger
        return logger


log = BotLogger.get_logger()


def info(msg):
    log.info(msg)


def warning(msg):
    log.warning(msg)


def error(msg):
    log.error(msg)


def debug(msg):
    log.debug(msg)


def buy(msg):
    log.info(f"[BUY] {msg}")


def sell(msg):
    log.info(f"[SELL] {msg}")


def scan(msg):
    log.info(f"[SCAN] {msg}")

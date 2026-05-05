"""Simple logger wrapper for Socratic Agents"""

import logging
from typing import Optional


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific component"""
    return logging.getLogger(f"socratic_agents.{name}")


def set_debug_mode(enabled: bool) -> None:
    """Toggle debug mode for all loggers"""
    level = logging.DEBUG if enabled else logging.ERROR
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    for logger_name in logging.Logger.manager.loggerDict:
        logger_obj = logging.getLogger(logger_name)
        if logger_obj:
            logger_obj.setLevel(level)


def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    root_logger = logging.getLogger()
    return root_logger.level == logging.DEBUG

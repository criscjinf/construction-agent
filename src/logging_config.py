"""
Centralized logging configuration
Provides colored, formatted logs with different levels based on DEBUG setting
"""

import logging
import os
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(debug: bool = False, log_file: str = None) -> logging.Logger:
    """
    Configure logging with console and optional file output.

    Args:
        debug: If True, shows DEBUG level logs. Otherwise INFO only.
        log_file: Optional file path for log output

    Returns:
        Configured logger instance
    """

    # Create logs directory if needed
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

    # Get root logger
    logger = logging.getLogger("construction_agent")
    logger.handlers.clear()  # Clear any existing handlers

    # Set level based on debug mode
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)

    # Format with colors for console
    if debug:
        console_format = (
            "%(asctime)s | "
            "%(levelname)-8s | "
            "%(name)-25s | "
            "%(funcName)-20s | "
            "%(message)s"
        )
    else:
        console_format = "%(levelname)-8s | %(name)-20s | %(message)s"

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(console_format, debug=debug)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_format = (
            "%(asctime)s | "
            "%(levelname)-8s | "
            "%(name)-25s | "
            "%(funcName)-20s | "
            "%(message)s"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
        file_formatter = logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


class ColoredFormatter(logging.Formatter):
    """Formatter with ANSI color codes for different log levels"""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"

    # Symbols
    SYMBOLS = {
        "DEBUG": "🔍",
        "INFO": "✅",
        "WARNING": "⚠️ ",
        "ERROR": "❌",
        "CRITICAL": "🚨",
    }

    def __init__(self, fmt, debug=False):
        super().__init__(fmt)
        self.debug = debug

    def format(self, record):
        if self.debug:
            # Add symbol and color
            symbol = self.COLORS.get(record.levelname, "")
            reset = self.RESET

            # Colorize level name
            record.levelname = f"{symbol}{record.levelname}{reset}"

            # Format the message
            result = super().format(record)
            return result
        else:
            return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module"""
    return logging.getLogger(f"construction_agent.{name}")

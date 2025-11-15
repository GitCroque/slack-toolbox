#!/usr/bin/env python3
"""
Logging configuration for Slack scripts
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str, log_file: str = None, level: str = 'INFO') -> logging.Logger:
    """
    Setup a logger with console and optional file output

    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Remove existing handlers
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Format for console (simpler)
    console_format = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)

        # Format for file (more detailed)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


def get_default_log_file(script_name: str) -> str:
    """
    Get default log file path for a script

    Args:
        script_name: Name of the script

    Returns:
        Log file path
    """
    timestamp = datetime.now().strftime('%Y%m%d')
    log_dir = Path(__file__).parent.parent / 'logs'
    return str(log_dir / f"{script_name}_{timestamp}.log")

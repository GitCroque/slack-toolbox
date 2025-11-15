"""
Slack Management Platform - Core Library
"""

from .slack_client import SlackManager
from .utils import *
from .logger import setup_logger, get_default_log_file

__all__ = ['SlackManager', 'setup_logger', 'get_default_log_file']

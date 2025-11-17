"""
Slack Management Platform - Core Library

Main exports:
- SlackManager: Slack API client wrapper
- Utility functions for CSV/JSON handling, formatting, validation
- Logger setup functions
- Validators for input validation
- Script base class for reducing boilerplate
"""

from .slack_client import SlackManager
from .logger import setup_logger, get_default_log_file

# Utility functions
from .utils import (
    save_to_csv,
    save_to_json,
    load_csv,
    load_json,
    load_config,
    format_timestamp,
    parse_timestamp,
    days_ago,
    confirm_action,
    print_table,
    progress_bar,
    sanitize_channel_name,
    get_user_display_name,
    format_bytes,
    batch_process,
    validate_email,
    create_backup_filename,
    ensure_directory,
)

# Validators
from .validators import (
    ValidationError,
    validate_email,
    validate_channel_name,
    sanitize_channel_name,
    validate_file_path,
    validate_csv_path,
    validate_output_directory,
    validate_positive_int,
    validate_range,
    validate_user_id,
    validate_channel_id,
    validate_webhook_url,
    validate_date_format,
)

# Script base class
from .script_base import SlackScript

# Alert system
from .alerts import Alert, AlertDetector, AlertManager

# Notifications
from .notifier import SlackWebhookNotifier, EmailNotifier, MultiNotifier

# PDF generation
from .pdf_generator import PDFReport

__version__ = "1.0.0"

__all__ = [
    # Core
    "SlackManager",
    "setup_logger",
    "get_default_log_file",
    # Script base
    "SlackScript",
    # Utils
    "save_to_csv",
    "save_to_json",
    "load_csv",
    "load_json",
    "load_config",
    "format_timestamp",
    "parse_timestamp",
    "days_ago",
    "confirm_action",
    "print_table",
    "progress_bar",
    "sanitize_channel_name",
    "get_user_display_name",
    "format_bytes",
    "batch_process",
    "validate_email",
    "create_backup_filename",
    "ensure_directory",
    # Validators
    "ValidationError",
    "validate_channel_name",
    "validate_file_path",
    "validate_csv_path",
    "validate_output_directory",
    "validate_positive_int",
    "validate_range",
    "validate_user_id",
    "validate_channel_id",
    "validate_webhook_url",
    "validate_date_format",
    # Alerts
    "Alert",
    "AlertDetector",
    "AlertManager",
    # Notifications
    "SlackWebhookNotifier",
    "EmailNotifier",
    "MultiNotifier",
    # PDF
    "PDFReport",
]

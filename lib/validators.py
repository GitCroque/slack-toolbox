"""
Input validation utilities for Slack management scripts.

Provides validation functions for various input types to prevent
security issues and invalid data processing.
"""

import os
import re
from pathlib import Path
from typing import Optional, Union


class ValidationError(ValueError):
    """Raised when input validation fails."""

    pass


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise

    Example:
        >>> validate_email('user@example.com')
        True
        >>> validate_email('invalid@email')
        False
    """
    if not email or not isinstance(email, str):
        return False

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def validate_channel_name(name: str) -> bool:
    """
    Validate Slack channel name format.

    Slack channel names must:
    - Be lowercase
    - Contain only letters, numbers, hyphens, underscores
    - Not exceed 80 characters
    - Not start/end with hyphen or underscore

    Args:
        name: Channel name to validate

    Returns:
        True if channel name is valid, False otherwise

    Example:
        >>> validate_channel_name('general-chat')
        True
        >>> validate_channel_name('Invalid Channel!')
        False
    """
    if not name or not isinstance(name, str):
        return False

    # Slack channel name rules
    if len(name) > 80:
        return False

    pattern = r"^[a-z0-9][a-z0-9_-]*[a-z0-9]$|^[a-z0-9]$"
    return bool(re.match(pattern, name.lower()))


def sanitize_channel_name(name: str) -> str:
    """
    Sanitize a string to make it a valid Slack channel name.

    Args:
        name: Raw channel name

    Returns:
        Sanitized channel name

    Raises:
        ValidationError: If name cannot be sanitized to valid format

    Example:
        >>> sanitize_channel_name('General Chat!')
        'general-chat'
        >>> sanitize_channel_name('__test__')
        'test'
    """
    if not name:
        raise ValidationError("Channel name cannot be empty")

    # Convert to lowercase
    name = name.lower()

    # Replace spaces and invalid chars with hyphens
    name = re.sub(r"[^a-z0-9_-]+", "-", name)

    # Remove leading/trailing hyphens and underscores
    name = name.strip("-_")

    # Collapse multiple hyphens
    name = re.sub(r"-+", "-", name)

    # Truncate to 80 chars
    name = name[:80]

    # Final validation
    if not validate_channel_name(name):
        raise ValidationError(f"Cannot sanitize '{name}' to valid channel name")

    return name


def validate_file_path(
    path: Union[str, Path],
    must_exist: bool = False,
    must_not_exist: bool = False,
    must_be_file: bool = False,
    must_be_dir: bool = False,
    allow_absolute_only: bool = False,
) -> Path:
    """
    Validate and sanitize file path.

    Args:
        path: File or directory path
        must_exist: Path must exist
        must_not_exist: Path must not exist
        must_be_file: Path must be a file (if exists)
        must_be_dir: Path must be a directory (if exists)
        allow_absolute_only: Only allow absolute paths

    Returns:
        Resolved Path object

    Raises:
        ValidationError: If validation fails

    Example:
        >>> validate_file_path('output.csv')
        PosixPath('/current/dir/output.csv')
        >>> validate_file_path('../../../etc/passwd')
        ValidationError: Path traversal detected
    """
    if not path:
        raise ValidationError("Path cannot be empty")

    # Convert to Path object
    path_obj = Path(path)

    # Check for path traversal attempts
    try:
        resolved = path_obj.resolve()

        # Additional safety check - reject if too many parent references
        if str(path).count("..") > 2:
            raise ValidationError("Excessive parent directory references")

    except (OSError, RuntimeError) as e:
        raise ValidationError(f"Invalid path: {e}")

    # Check absolute path requirement
    if allow_absolute_only and not path_obj.is_absolute():
        raise ValidationError("Only absolute paths are allowed")

    # Check existence requirements
    if must_exist and not resolved.exists():
        raise ValidationError(f"Path does not exist: {path}")

    if must_not_exist and resolved.exists():
        raise ValidationError(f"Path already exists: {path}")

    # Check type requirements
    if must_be_file and resolved.exists() and not resolved.is_file():
        raise ValidationError(f"Path is not a file: {path}")

    if must_be_dir and resolved.exists() and not resolved.is_dir():
        raise ValidationError(f"Path is not a directory: {path}")

    return resolved


def validate_csv_path(path: Union[str, Path], must_exist: bool = True) -> Path:
    """
    Validate CSV file path.

    Args:
        path: Path to CSV file
        must_exist: Whether file must exist

    Returns:
        Validated Path object

    Raises:
        ValidationError: If validation fails

    Example:
        >>> validate_csv_path('users.csv')
        PosixPath('/current/dir/users.csv')
    """
    validated_path = validate_file_path(path, must_exist=must_exist, must_be_file=must_exist if must_exist else False)

    # Check extension
    if validated_path.suffix.lower() not in [".csv", ""]:
        raise ValidationError(f"File must have .csv extension: {path}")

    return validated_path


def validate_output_directory(path: Union[str, Path], create: bool = False) -> Path:
    """
    Validate output directory path.

    Args:
        path: Directory path
        create: Create directory if it doesn't exist

    Returns:
        Validated Path object

    Raises:
        ValidationError: If validation fails

    Example:
        >>> validate_output_directory('backups', create=True)
        PosixPath('/current/dir/backups')
    """
    validated_path = validate_file_path(path)

    if not validated_path.exists():
        if create:
            try:
                validated_path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise ValidationError(f"Cannot create directory: {e}")
        else:
            raise ValidationError(f"Directory does not exist: {path}")

    elif not validated_path.is_dir():
        raise ValidationError(f"Path is not a directory: {path}")

    return validated_path


def validate_positive_int(value: Union[int, str], name: str = "value") -> int:
    """
    Validate positive integer value.

    Args:
        value: Value to validate
        name: Name of the value (for error messages)

    Returns:
        Validated integer

    Raises:
        ValidationError: If validation fails

    Example:
        >>> validate_positive_int('30', 'days')
        30
        >>> validate_positive_int(-5, 'count')
        ValidationError: count must be positive
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{name} must be an integer")

    if int_value <= 0:
        raise ValidationError(f"{name} must be positive")

    return int_value


def validate_range(value: Union[int, float], min_val: Optional[float] = None, max_val: Optional[float] = None, name: str = "value") -> Union[int, float]:
    """
    Validate value is within range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        name: Name of the value (for error messages)

    Returns:
        Validated value

    Raises:
        ValidationError: If validation fails

    Example:
        >>> validate_range(50, min_val=0, max_val=100, name='percentage')
        50
        >>> validate_range(150, max_val=100, name='percentage')
        ValidationError: percentage must be <= 100
    """
    if min_val is not None and value < min_val:
        raise ValidationError(f"{name} must be >= {min_val}")

    if max_val is not None and value > max_val:
        raise ValidationError(f"{name} must be <= {max_val}")

    return value


def validate_user_id(user_id: str) -> str:
    """
    Validate Slack user ID format.

    Slack user IDs typically start with 'U' followed by uppercase letters/numbers.

    Args:
        user_id: User ID to validate

    Returns:
        Validated user ID

    Raises:
        ValidationError: If validation fails

    Example:
        >>> validate_user_id('U1234ABCD')
        'U1234ABCD'
        >>> validate_user_id('invalid')
        ValidationError: Invalid user ID format
    """
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID cannot be empty")

    # Slack user ID pattern
    pattern = r"^U[A-Z0-9]{8,}$"
    if not re.match(pattern, user_id.upper()):
        raise ValidationError(f"Invalid user ID format: {user_id}")

    return user_id.upper()


def validate_channel_id(channel_id: str) -> str:
    """
    Validate Slack channel ID format.

    Slack channel IDs typically start with 'C' followed by uppercase letters/numbers.

    Args:
        channel_id: Channel ID to validate

    Returns:
        Validated channel ID

    Raises:
        ValidationError: If validation fails

    Example:
        >>> validate_channel_id('C1234ABCD')
        'C1234ABCD'
        >>> validate_channel_id('invalid')
        ValidationError: Invalid channel ID format
    """
    if not channel_id or not isinstance(channel_id, str):
        raise ValidationError("Channel ID cannot be empty")

    # Slack channel ID pattern (C for public, G for private/groups)
    pattern = r"^[CG][A-Z0-9]{8,}$"
    if not re.match(pattern, channel_id.upper()):
        raise ValidationError(f"Invalid channel ID format: {channel_id}")

    return channel_id.upper()


def validate_webhook_url(url: str) -> str:
    """
    Validate Slack webhook URL format.

    Args:
        url: Webhook URL to validate

    Returns:
        Validated webhook URL

    Raises:
        ValidationError: If validation fails

    Example:
        >>> validate_webhook_url('https://hooks.slack.com/services/T00/B00/xxx')
        'https://hooks.slack.com/services/T00/B00/xxx'
    """
    if not url or not isinstance(url, str):
        raise ValidationError("Webhook URL cannot be empty")

    # Must be HTTPS
    if not url.startswith("https://"):
        raise ValidationError("Webhook URL must use HTTPS")

    # Must be hooks.slack.com
    if "hooks.slack.com/services/" not in url:
        raise ValidationError("Invalid Slack webhook URL format")

    return url


def validate_date_format(date_str: str, format: str = "%Y-%m-%d") -> str:
    """
    Validate date string format.

    Args:
        date_str: Date string to validate
        format: Expected date format (default: YYYY-MM-DD)

    Returns:
        Validated date string

    Raises:
        ValidationError: If validation fails

    Example:
        >>> validate_date_format('2024-01-15')
        '2024-01-15'
        >>> validate_date_format('15/01/2024')
        ValidationError: Invalid date format
    """
    from datetime import datetime

    try:
        datetime.strptime(date_str, format)
        return date_str
    except ValueError:
        raise ValidationError(f"Invalid date format. Expected: {format}")

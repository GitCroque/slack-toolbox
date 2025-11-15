#!/usr/bin/env python3
"""
Utility functions for Slack scripts
"""

import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import time


def save_to_csv(data: List[Dict], filename: str, fieldnames: Optional[List[str]] = None):
    """
    Save data to CSV file

    Args:
        data: List of dictionaries to save
        filename: Output filename
        fieldnames: List of field names. If None, uses keys from first item
    """
    if not data:
        print("⚠️  No data to save")
        return

    if fieldnames is None:
        fieldnames = list(data[0].keys())

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Saved {len(data)} rows to {filename}")


def save_to_json(data: Any, filename: str, pretty: bool = True):
    """
    Save data to JSON file

    Args:
        data: Data to save (dict, list, etc.)
        filename: Output filename
        pretty: Pretty-print JSON with indentation
    """
    with open(filename, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, f, ensure_ascii=False)

    print(f"✅ Saved data to {filename}")


def load_csv(filename: str) -> List[Dict]:
    """
    Load data from CSV file

    Args:
        filename: Input filename

    Returns:
        List of dictionaries
    """
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    print(f"📁 Loaded {len(data)} rows from {filename}")
    return data


def load_json(filename: str) -> Any:
    """
    Load data from JSON file

    Args:
        filename: Input filename

    Returns:
        Parsed JSON data
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📁 Loaded data from {filename}")
    return data


def format_timestamp(ts: float) -> str:
    """
    Format Unix timestamp to readable date

    Args:
        ts: Unix timestamp

    Returns:
        Formatted date string
    """
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def parse_timestamp(date_str: str) -> float:
    """
    Parse date string to Unix timestamp

    Args:
        date_str: Date string (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)

    Returns:
        Unix timestamp
    """
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        dt = datetime.strptime(date_str, '%Y-%m-%d')

    return dt.timestamp()


def days_ago(days: int) -> float:
    """
    Get Unix timestamp for N days ago

    Args:
        days: Number of days

    Returns:
        Unix timestamp
    """
    dt = datetime.now() - timedelta(days=days)
    return dt.timestamp()


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user for confirmation

    Args:
        message: Confirmation message
        default: Default response if user just presses Enter

    Returns:
        True if user confirms, False otherwise
    """
    choices = " [Y/n]" if default else " [y/N]"
    response = input(message + choices + ": ").strip().lower()

    if not response:
        return default

    return response in ['y', 'yes', 'oui']


def print_table(data: List[Dict], headers: Optional[List[str]] = None, max_width: int = 100):
    """
    Print data as a formatted table

    Args:
        data: List of dictionaries
        headers: List of headers to display. If None, uses all keys
        max_width: Maximum width for each column
    """
    if not data:
        print("No data to display")
        return

    if headers is None:
        headers = list(data[0].keys())

    # Calculate column widths
    widths = {}
    for header in headers:
        widths[header] = min(
            max(len(str(header)), max(len(str(row.get(header, ''))) for row in data)),
            max_width
        )

    # Print header
    header_line = " | ".join(str(h).ljust(widths[h]) for h in headers)
    print(header_line)
    print("-" * len(header_line))

    # Print rows
    for row in data:
        line = " | ".join(str(row.get(h, '')).ljust(widths[h])[:widths[h]] for h in headers)
        print(line)


def progress_bar(current: int, total: int, prefix: str = '', suffix: str = '', length: int = 50):
    """
    Display a progress bar

    Args:
        current: Current progress
        total: Total items
        prefix: Prefix string
        suffix: Suffix string
        length: Length of progress bar
    """
    percent = 100 * (current / float(total))
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)

    print(f'\r{prefix} |{bar}| {percent:.1f}% {suffix}', end='')

    if current == total:
        print()


def sanitize_channel_name(name: str) -> str:
    """
    Sanitize channel name to follow Slack naming rules

    Args:
        name: Channel name

    Returns:
        Sanitized channel name (lowercase, alphanumeric, hyphens, underscores)
    """
    # Convert to lowercase
    name = name.lower()

    # Replace spaces with hyphens
    name = name.replace(' ', '-')

    # Keep only alphanumeric, hyphens, and underscores
    name = ''.join(c for c in name if c.isalnum() or c in ['-', '_'])

    # Limit to 80 characters
    name = name[:80]

    # Remove leading/trailing hyphens
    name = name.strip('-')

    return name


def get_user_display_name(user: Dict) -> str:
    """
    Get best display name for a user

    Args:
        user: User dictionary from Slack API

    Returns:
        Display name
    """
    profile = user.get('profile', {})

    if profile.get('display_name'):
        return profile['display_name']
    elif profile.get('real_name'):
        return profile['real_name']
    elif user.get('real_name'):
        return user['real_name']
    else:
        return user.get('name', 'Unknown')


def format_bytes(bytes_size: int) -> str:
    """
    Format bytes to human-readable size

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def batch_process(items: List[Any], batch_size: int = 50, delay: float = 1.0):
    """
    Generator to process items in batches with delay

    Args:
        items: List of items to process
        batch_size: Number of items per batch
        delay: Delay in seconds between batches

    Yields:
        Batches of items
    """
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        yield batch

        # Add delay between batches (except after last batch)
        if i + batch_size < len(items):
            time.sleep(delay)


def validate_email(email: str) -> bool:
    """
    Basic email validation

    Args:
        email: Email address to validate

    Returns:
        True if email format is valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def create_backup_filename(base_name: str, extension: str = 'json') -> str:
    """
    Create a timestamped backup filename

    Args:
        base_name: Base name for the file
        extension: File extension (without dot)

    Returns:
        Filename with timestamp
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_name}_{timestamp}.{extension}"


def ensure_directory(path: str):
    """
    Ensure a directory exists, create if it doesn't

    Args:
        path: Directory path
    """
    Path(path).mkdir(parents=True, exist_ok=True)

#!/usr/bin/env python3
"""
Generate report on files shared in Slack workspace
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import save_to_csv, print_table, format_bytes, format_timestamp
from lib.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(description='Generate Slack files report')
    parser.add_argument('--user', help='Filter by user email')
    parser.add_argument('--channel', help='Filter by channel name')
    parser.add_argument('--limit', type=int, default=100,
                       help='Number of files to retrieve (default: 100)')
    parser.add_argument('--export', help='Export to CSV file')

    args = parser.parse_args()

    logger = setup_logger('file_report')

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get user ID if email provided
        user_id = None
        if args.user:
            user = slack.get_user_by_email(args.user)
            if not user:
                logger.error(f"User not found: {args.user}")
                sys.exit(1)
            user_id = user['id']

        # Get channel ID if name provided
        channel_id = None
        if args.channel:
            channels = slack.list_channels(include_private=True)
            channel = next((ch for ch in channels if ch['name'] == args.channel), None)
            if not channel:
                logger.error(f"Channel not found: #{args.channel}")
                sys.exit(1)
            channel_id = channel['id']

        # Get files
        logger.info("Fetching files...")
        files = slack.list_files(
            user_id=user_id,
            channel_id=channel_id,
            count=args.limit
        )

        logger.info(f"Found {len(files)} files")

        if not files:
            print("No files found")
            return

        # Get user info for mapping
        users = slack.list_users()
        user_map = {u['id']: u for u in users}

        # Format file data
        file_data = []
        total_size = 0

        for file in files:
            user = user_map.get(file.get('user'), {})
            profile = user.get('profile', {})

            file_info = {
                'name': file.get('name', 'Unnamed'),
                'title': file.get('title', '')[:50],
                'type': file.get('filetype', 'unknown'),
                'size': format_bytes(file.get('size', 0)),
                'size_bytes': file.get('size', 0),
                'user': profile.get('display_name') or profile.get('real_name') or user.get('name', 'Unknown'),
                'created': format_timestamp(file.get('created', 0)),
                'is_public': file.get('is_public', False),
                'url': file.get('url_private', '')
            }

            total_size += file.get('size', 0)
            file_data.append(file_info)

        # Sort by size (descending)
        file_data.sort(key=lambda x: x['size_bytes'], reverse=True)

        # Display or export
        if args.export:
            # Remove size_bytes for CSV export (keep formatted size)
            for item in file_data:
                del item['size_bytes']
            save_to_csv(file_data, args.export)
        else:
            headers = ['name', 'type', 'size', 'user', 'created', 'is_public']
            print_table(file_data, headers=headers)

            print(f"\nTotal files: {len(files)}")
            print(f"Total size: {format_bytes(total_size)}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

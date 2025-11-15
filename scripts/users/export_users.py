#!/usr/bin/env python3
"""
Export all Slack users to CSV or JSON
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import save_to_csv, save_to_json, get_user_display_name, format_timestamp
from lib.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(description='Export Slack users')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv',
                       help='Export format (default: csv)')
    parser.add_argument('--output', help='Output filename')
    parser.add_argument('--include-deleted', action='store_true',
                       help='Include deactivated users')
    parser.add_argument('--include-bots', action='store_true',
                       help='Include bot users')
    parser.add_argument('--full', action='store_true',
                       help='Include all user fields (full export)')

    args = parser.parse_args()

    logger = setup_logger('export_users')

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get all users
        logger.info("Fetching users...")
        users = slack.list_users(include_deleted=args.include_deleted)

        # Filter and format users
        export_data = []

        for user in users:
            # Skip bots unless requested
            if user.get('is_bot') and not args.include_bots:
                continue

            profile = user.get('profile', {})

            # Basic user info
            user_data = {
                'user_id': user.get('id'),
                'username': user.get('name'),
                'email': profile.get('email', ''),
                'real_name': profile.get('real_name', ''),
                'display_name': get_user_display_name(user),
                'first_name': profile.get('first_name', ''),
                'last_name': profile.get('last_name', ''),
                'status': 'Deactivated' if user.get('deleted') else 'Active',
                'is_admin': user.get('is_admin', False),
                'is_owner': user.get('is_owner', False),
                'is_bot': user.get('is_bot', False),
                'is_guest': user.get('is_restricted', False) or user.get('is_ultra_restricted', False),
            }

            if args.full:
                # Add additional fields for full export
                user_data.update({
                    'title': profile.get('title', ''),
                    'phone': profile.get('phone', ''),
                    'skype': profile.get('skype', ''),
                    'timezone': user.get('tz', ''),
                    'timezone_label': user.get('tz_label', ''),
                    'timezone_offset': user.get('tz_offset', ''),
                    'locale': user.get('locale', ''),
                    'team_id': user.get('team_id', ''),
                    'updated': format_timestamp(user.get('updated', 0)),
                    'has_2fa': user.get('has_2fa', False),
                    'profile_image': profile.get('image_192', ''),
                })

            export_data.append(user_data)

        logger.info(f"Exporting {len(export_data)} users...")

        # Generate output filename if not specified
        if not args.output:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            args.output = f"slack_users_{timestamp}.{args.format}"

        # Export
        if args.format == 'csv':
            save_to_csv(export_data, args.output)
        else:
            save_to_json(export_data, args.output)

        logger.info(f"✅ Successfully exported {len(export_data)} users to {args.output}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

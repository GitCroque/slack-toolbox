#!/usr/bin/env python3
"""
List all users in the Slack workspace with details
"""

import argparse
import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import print_table, save_to_csv, save_to_json, get_user_display_name
from lib.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(description='List all Slack users')
    parser.add_argument('--include-deleted', action='store_true',
                       help='Include deactivated users')
    parser.add_argument('--include-bots', action='store_true',
                       help='Include bot users')
    parser.add_argument('--role', choices=['admin', 'owner', 'member', 'guest'],
                       help='Filter by role')
    parser.add_argument('--export', choices=['csv', 'json'],
                       help='Export to file format')
    parser.add_argument('--output', help='Output filename for export')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed information')

    args = parser.parse_args()

    logger = setup_logger('list_users')

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get all users
        logger.info("Fetching users...")
        users = slack.list_users(include_deleted=args.include_deleted)

        # Filter users
        filtered_users = []
        for user in users:
            # Skip bots unless requested
            if user.get('is_bot') and not args.include_bots:
                continue

            # Filter by role
            if args.role:
                if args.role == 'admin' and not user.get('is_admin'):
                    continue
                elif args.role == 'owner' and not user.get('is_owner'):
                    continue
                elif args.role == 'guest' and not (user.get('is_restricted') or user.get('is_ultra_restricted')):
                    continue
                elif args.role == 'member' and (user.get('is_admin') or user.get('is_owner') or
                                               user.get('is_restricted') or user.get('is_ultra_restricted')):
                    continue

            filtered_users.append(user)

        logger.info(f"Found {len(filtered_users)} users")

        # Prepare data for display/export
        user_data = []
        for user in filtered_users:
            profile = user.get('profile', {})

            # Determine role
            if user.get('is_owner'):
                role = 'Owner'
            elif user.get('is_admin'):
                role = 'Admin'
            elif user.get('is_ultra_restricted'):
                role = 'Single-Channel Guest'
            elif user.get('is_restricted'):
                role = 'Multi-Channel Guest'
            else:
                role = 'Member'

            # Determine status
            if user.get('deleted'):
                status = 'Deactivated'
            elif user.get('is_bot'):
                status = 'Bot'
            else:
                status = 'Active'

            user_info = {
                'id': user.get('id'),
                'name': user.get('name'),
                'display_name': get_user_display_name(user),
                'real_name': profile.get('real_name', ''),
                'email': profile.get('email', ''),
                'role': role,
                'status': status,
                'timezone': user.get('tz_label', ''),
            }

            if args.verbose:
                user_info.update({
                    'title': profile.get('title', ''),
                    'phone': profile.get('phone', ''),
                    'updated': user.get('updated', ''),
                })

            user_data.append(user_info)

        # Export or display
        if args.export == 'csv':
            output_file = args.output or 'users_export.csv'
            save_to_csv(user_data, output_file)
        elif args.export == 'json':
            output_file = args.output or 'users_export.json'
            save_to_json(user_data, output_file)
        else:
            # Display as table
            headers = ['name', 'display_name', 'email', 'role', 'status']
            if args.verbose:
                headers.extend(['title', 'timezone'])

            print_table(user_data, headers=headers)
            print(f"\nTotal: {len(user_data)} users")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Find users who haven't been active in X days
Note: This requires Slack audit logs (Enterprise Grid only) or manual message checking
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import days_ago, print_table, save_to_csv
from lib.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(
        description='Find inactive Slack users (basic check using profile updates)'
    )
    parser.add_argument('--days', type=int, default=60,
                       help='Number of days of inactivity (default: 60)')
    parser.add_argument('--export', help='Export results to CSV file')
    parser.add_argument('--include-guests', action='store_true',
                       help='Include guest users')

    args = parser.parse_args()

    logger = setup_logger('inactive_users')

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get all users
        logger.info("Fetching users...")
        users = slack.list_users()

        # Calculate cutoff timestamp
        cutoff_ts = days_ago(args.days)

        # Find inactive users (using last profile update as proxy)
        logger.info(f"Checking for users inactive for {args.days}+ days...")
        inactive_users = []

        for user in users:
            # Skip bots
            if user.get('is_bot'):
                continue

            # Skip guests unless requested
            is_guest = user.get('is_restricted') or user.get('is_ultra_restricted')
            if is_guest and not args.include_guests:
                continue

            # Check last update time
            last_update = user.get('updated', 0)

            if last_update < cutoff_ts:
                profile = user.get('profile', {})
                days_inactive = int((datetime.now().timestamp() - last_update) / 86400)

                # Determine role
                if user.get('is_owner'):
                    role = 'Owner'
                elif user.get('is_admin'):
                    role = 'Admin'
                elif is_guest:
                    role = 'Guest'
                else:
                    role = 'Member'

                inactive_users.append({
                    'id': user['id'],
                    'name': user.get('name'),
                    'email': profile.get('email', ''),
                    'real_name': profile.get('real_name', ''),
                    'role': role,
                    'days_inactive': days_inactive,
                    'last_update': datetime.fromtimestamp(last_update).strftime('%Y-%m-%d')
                })

        # Sort by days inactive (descending)
        inactive_users.sort(key=lambda x: x['days_inactive'], reverse=True)

        logger.info(f"\nFound {len(inactive_users)} potentially inactive users")

        # Display or export results
        if inactive_users:
            if args.export:
                save_to_csv(inactive_users, args.export)
            else:
                headers = ['name', 'email', 'role', 'days_inactive', 'last_update']
                print_table(inactive_users, headers=headers)

            print(f"\n⚠️  Note: This uses profile update time as a proxy for activity.")
            print(f"   For accurate activity data, use Slack's Analytics dashboard or Enterprise Grid audit logs.")
        else:
            print(f"No inactive users found ({args.days}+ days)")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

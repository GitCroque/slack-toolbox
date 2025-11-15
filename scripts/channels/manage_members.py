#!/usr/bin/env python3
"""
Manage channel members (add or remove users)
"""

import argparse
import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import progress_bar
from lib.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(
        description='Manage Slack channel members',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add users to channel
  python3 manage_members.py --channel general --add user1@example.com,user2@example.com

  # Remove user from channel
  python3 manage_members.py --channel general --remove user@example.com

  # Add all admins to a channel
  python3 manage_members.py --channel leadership --add-admins
        """
    )

    parser.add_argument('--channel', required=True,
                       help='Channel name')
    parser.add_argument('--add', help='Comma-separated list of emails to add')
    parser.add_argument('--remove', help='Comma-separated list of emails to remove')
    parser.add_argument('--add-admins', action='store_true',
                       help='Add all workspace admins to channel')

    args = parser.parse_args()

    logger = setup_logger('manage_members')

    if not args.add and not args.remove and not args.add_admins:
        parser.error("At least one of --add, --remove, or --add-admins must be specified")

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get channel
        logger.info(f"Looking up channel: #{args.channel}")
        channels = slack.list_channels(include_private=True)
        channel = next((ch for ch in channels if ch['name'] == args.channel), None)

        if not channel:
            logger.error(f"Channel not found: #{args.channel}")
            sys.exit(1)

        channel_id = channel['id']

        # Add members
        if args.add or args.add_admins:
            user_ids_to_add = []

            if args.add_admins:
                logger.info("Finding all admins...")
                all_users = slack.list_users()
                admin_users = [u for u in all_users if u.get('is_admin') or u.get('is_owner')]
                user_ids_to_add.extend([u['id'] for u in admin_users])
                logger.info(f"Found {len(admin_users)} admins")

            if args.add:
                emails = [e.strip() for e in args.add.split(',')]
                logger.info(f"Looking up {len(emails)} users...")

                for email in emails:
                    user = slack.get_user_by_email(email)
                    if user:
                        user_ids_to_add.append(user['id'])
                    else:
                        logger.warning(f"User not found: {email}")

            if user_ids_to_add:
                logger.info(f"Adding {len(user_ids_to_add)} users to #{args.channel}...")

                # Add in batches (Slack API limit)
                batch_size = 30
                for i in range(0, len(user_ids_to_add), batch_size):
                    batch = user_ids_to_add[i:i+batch_size]
                    try:
                        slack.invite_to_channel(channel_id, batch)
                        logger.info(f"Added {len(batch)} users")
                    except Exception as e:
                        logger.error(f"Failed to add batch: {e}")

                logger.info(f"✅ Successfully added users to #{args.channel}")

        # Remove members
        if args.remove:
            emails = [e.strip() for e in args.remove.split(',')]
            logger.info(f"Looking up {len(emails)} users to remove...")

            removed_count = 0
            for email in emails:
                user = slack.get_user_by_email(email)
                if not user:
                    logger.warning(f"User not found: {email}")
                    continue

                try:
                    slack.remove_from_channel(channel_id, user['id'])
                    logger.info(f"Removed {email}")
                    removed_count += 1
                except Exception as e:
                    logger.error(f"Failed to remove {email}: {e}")

            logger.info(f"✅ Successfully removed {removed_count} users from #{args.channel}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

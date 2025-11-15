#!/usr/bin/env python3
"""
Invite users to Slack workspace from CSV file or command line
"""

import argparse
import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import load_csv, progress_bar, validate_email
from lib.logger import setup_logger


def invite_user(slack: SlackManager, email: str, first_name: str = None,
               last_name: str = None, channels: list = None, logger=None):
    """Invite a single user"""
    try:
        # Check if user already exists
        existing_user = slack.get_user_by_email(email)
        if existing_user:
            logger.warning(f"User {email} already exists")
            return False

        # Invite user
        result = slack.invite_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            channels=channels
        )

        logger.info(f"✅ Invited {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to invite {email}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Invite users to Slack workspace',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Invite from CSV file
  python3 invite_users.py --file users.csv

  # Invite single user
  python3 invite_users.py --email user@example.com --first-name John --last-name Doe

  # Invite user and add to channels
  python3 invite_users.py --email user@example.com --channels general,random

CSV format:
  email,first_name,last_name,channels
  john@example.com,John,Doe,"general,random"
  jane@example.com,Jane,Smith,general
        """
    )

    parser.add_argument('--file', help='CSV file with users to invite')
    parser.add_argument('--email', help='Single email address to invite')
    parser.add_argument('--first-name', help='First name (for single user)')
    parser.add_argument('--last-name', help='Last name (for single user)')
    parser.add_argument('--channels', help='Comma-separated list of channel names')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without actually inviting')

    args = parser.parse_args()

    logger = setup_logger('invite_users')

    # Validate arguments
    if not args.file and not args.email:
        parser.error("Either --file or --email must be specified")

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get channel IDs if specified
        channel_ids = None
        if args.channels:
            logger.info("Looking up channel IDs...")
            all_channels = slack.list_channels(include_private=True)
            channel_names = [c.strip() for c in args.channels.split(',')]
            channel_map = {ch['name']: ch['id'] for ch in all_channels}

            channel_ids = []
            for name in channel_names:
                if name in channel_map:
                    channel_ids.append(channel_map[name])
                else:
                    logger.warning(f"Channel '{name}' not found")

        # Process invitations
        users_to_invite = []

        if args.file:
            # Load from CSV
            logger.info(f"Loading users from {args.file}")
            rows = load_csv(args.file)

            for row in rows:
                email = row.get('email', '').strip()
                if not email:
                    continue

                if not validate_email(email):
                    logger.warning(f"Invalid email: {email}")
                    continue

                user_channels = channel_ids
                if 'channels' in row and row['channels']:
                    # Get channel IDs for this user's channels
                    user_channel_names = [c.strip() for c in row['channels'].split(',')]
                    all_channels = slack.list_channels(include_private=True)
                    channel_map = {ch['name']: ch['id'] for ch in all_channels}
                    user_channels = [channel_map[name] for name in user_channel_names
                                   if name in channel_map]

                users_to_invite.append({
                    'email': email,
                    'first_name': row.get('first_name'),
                    'last_name': row.get('last_name'),
                    'channels': user_channels
                })

        else:
            # Single user from command line
            if not validate_email(args.email):
                logger.error(f"Invalid email: {args.email}")
                sys.exit(1)

            users_to_invite.append({
                'email': args.email,
                'first_name': args.first_name,
                'last_name': args.last_name,
                'channels': channel_ids
            })

        logger.info(f"Found {len(users_to_invite)} users to invite")

        if args.dry_run:
            logger.info("DRY RUN - No invitations will be sent")
            for user in users_to_invite:
                logger.info(f"Would invite: {user['email']}")
            sys.exit(0)

        # Invite users
        success_count = 0
        failed_count = 0

        for i, user in enumerate(users_to_invite, 1):
            progress_bar(i, len(users_to_invite), prefix='Inviting users')

            if invite_user(slack, logger=logger, **user):
                success_count += 1
            else:
                failed_count += 1

        print()
        logger.info(f"✅ Successfully invited: {success_count}")
        if failed_count > 0:
            logger.warning(f"❌ Failed: {failed_count}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

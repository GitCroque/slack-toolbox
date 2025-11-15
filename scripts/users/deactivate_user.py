#!/usr/bin/env python3
"""
Deactivate a Slack user
"""

import argparse
import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import confirm_action
from lib.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(description='Deactivate a Slack user')
    parser.add_argument('--email', help='User email address')
    parser.add_argument('--user-id', help='User ID (alternative to email)')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompt')

    args = parser.parse_args()

    if not args.email and not args.user_id:
        parser.error("Either --email or --user-id must be specified")

    logger = setup_logger('deactivate_user')

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get user
        if args.email:
            logger.info(f"Looking up user by email: {args.email}")
            user = slack.get_user_by_email(args.email)
            if not user:
                logger.error(f"User not found: {args.email}")
                sys.exit(1)
        else:
            # Get user by ID
            users = slack.list_users()
            user = next((u for u in users if u['id'] == args.user_id), None)
            if not user:
                logger.error(f"User not found: {args.user_id}")
                sys.exit(1)

        user_id = user['id']
        profile = user.get('profile', {})
        display_name = profile.get('display_name') or profile.get('real_name') or user.get('name')

        # Check if already deactivated
        if user.get('deleted'):
            logger.warning(f"User {display_name} is already deactivated")
            sys.exit(0)

        # Confirm action
        if not args.force:
            if not confirm_action(f"Are you sure you want to deactivate {display_name} ({profile.get('email', '')})?"):
                logger.info("Cancelled")
                sys.exit(0)

        # Deactivate user
        logger.info(f"Deactivating user: {display_name}")
        slack.deactivate_user(user_id)

        logger.info(f"✅ Successfully deactivated {display_name}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

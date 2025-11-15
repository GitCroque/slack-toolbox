#!/usr/bin/env python3
"""
Archive or unarchive Slack channels
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
    parser = argparse.ArgumentParser(description='Archive or unarchive Slack channels')
    parser.add_argument('--name', help='Channel name')
    parser.add_argument('--channel-id', help='Channel ID (alternative to name)')
    parser.add_argument('--unarchive', action='store_true',
                       help='Unarchive instead of archive')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompt')

    args = parser.parse_args()

    if not args.name and not args.channel_id:
        parser.error("Either --name or --channel-id must be specified")

    logger = setup_logger('archive_channel')

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get channel
        if args.name:
            logger.info(f"Looking up channel: #{args.name}")
            channels = slack.list_channels(include_private=True, include_archived=True)
            channel = next((ch for ch in channels if ch['name'] == args.name), None)
            if not channel:
                logger.error(f"Channel not found: #{args.name}")
                sys.exit(1)
        else:
            channels = slack.list_channels(include_private=True, include_archived=True)
            channel = next((ch for ch in channels if ch['id'] == args.channel_id), None)
            if not channel:
                logger.error(f"Channel not found: {args.channel_id}")
                sys.exit(1)

        channel_id = channel['id']
        channel_name = channel['name']
        is_archived = channel.get('is_archived', False)

        # Check current status
        if args.unarchive:
            if not is_archived:
                logger.warning(f"Channel #{channel_name} is not archived")
                sys.exit(0)
            action = "unarchive"
        else:
            if is_archived:
                logger.warning(f"Channel #{channel_name} is already archived")
                sys.exit(0)
            action = "archive"

        # Confirm action
        if not args.force:
            if not confirm_action(f"Are you sure you want to {action} #{channel_name}?"):
                logger.info("Cancelled")
                sys.exit(0)

        # Perform action
        logger.info(f"{action.capitalize()}ing channel: #{channel_name}")

        if args.unarchive:
            slack.unarchive_channel(channel_id)
            logger.info(f"✅ Successfully unarchived #{channel_name}")
        else:
            slack.archive_channel(channel_id)
            logger.info(f"✅ Successfully archived #{channel_name}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

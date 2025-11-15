#!/usr/bin/env python3
"""
Create Slack channels from CSV file or command line
"""

import argparse
import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import load_csv, sanitize_channel_name, progress_bar
from lib.logger import setup_logger


def create_channel(slack: SlackManager, name: str, description: str = None,
                  is_private: bool = False, logger=None):
    """Create a single channel"""
    try:
        # Sanitize channel name
        sanitized_name = sanitize_channel_name(name)

        if sanitized_name != name:
            logger.info(f"Channel name sanitized: '{name}' -> '{sanitized_name}'")

        # Check if channel already exists
        existing_channels = slack.list_channels(include_private=True)
        if any(ch['name'] == sanitized_name for ch in existing_channels):
            logger.warning(f"Channel '{sanitized_name}' already exists")
            return False

        # Create channel
        channel = slack.create_channel(
            name=sanitized_name,
            is_private=is_private,
            description=description
        )

        logger.info(f"✅ Created channel: #{sanitized_name}")
        return True

    except Exception as e:
        logger.error(f"Failed to create channel '{name}': {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Create Slack channels',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create from CSV file
  python3 create_channels.py --file channels.csv

  # Create single channel
  python3 create_channels.py --name project-alpha --description "Alpha project discussion"

  # Create private channel
  python3 create_channels.py --name confidential --private

CSV format:
  name,description,private
  project-alpha,"Alpha project discussion",false
  team-leads,"Leadership team",true
        """
    )

    parser.add_argument('--file', help='CSV file with channels to create')
    parser.add_argument('--name', help='Channel name (for single channel)')
    parser.add_argument('--description', help='Channel description')
    parser.add_argument('--private', action='store_true',
                       help='Create as private channel')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without actually creating')

    args = parser.parse_args()

    logger = setup_logger('create_channels')

    # Validate arguments
    if not args.file and not args.name:
        parser.error("Either --file or --name must be specified")

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Prepare channels to create
        channels_to_create = []

        if args.file:
            # Load from CSV
            logger.info(f"Loading channels from {args.file}")
            rows = load_csv(args.file)

            for row in rows:
                name = row.get('name', '').strip()
                if not name:
                    continue

                is_private = row.get('private', '').lower() in ['true', '1', 'yes']

                channels_to_create.append({
                    'name': name,
                    'description': row.get('description', ''),
                    'is_private': is_private
                })

        else:
            # Single channel from command line
            channels_to_create.append({
                'name': args.name,
                'description': args.description,
                'is_private': args.private
            })

        logger.info(f"Found {len(channels_to_create)} channels to create")

        if args.dry_run:
            logger.info("DRY RUN - No channels will be created")
            for channel in channels_to_create:
                ch_type = "private" if channel['is_private'] else "public"
                logger.info(f"Would create {ch_type} channel: #{channel['name']}")
            sys.exit(0)

        # Create channels
        success_count = 0
        failed_count = 0

        for i, channel in enumerate(channels_to_create, 1):
            progress_bar(i, len(channels_to_create), prefix='Creating channels')

            if create_channel(slack, logger=logger, **channel):
                success_count += 1
            else:
                failed_count += 1

        print()
        logger.info(f"✅ Successfully created: {success_count}")
        if failed_count > 0:
            logger.warning(f"❌ Failed: {failed_count}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

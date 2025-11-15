#!/usr/bin/env python3
"""
Create a full backup of Slack workspace data
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import save_to_json, ensure_directory
from lib.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(description='Create full Slack workspace backup')
    parser.add_argument('--output-dir', default='backups',
                       help='Output directory for backup (default: backups)')
    parser.add_argument('--include-messages', action='store_true',
                       help='Include message history (slower, much larger)')
    parser.add_argument('--message-limit', type=int, default=100,
                       help='Max messages per channel (default: 100)')

    args = parser.parse_args()

    logger = setup_logger('full_backup')

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Create backup directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(args.output_dir) / f"slack_backup_{timestamp}"
        ensure_directory(str(backup_dir))

        logger.info(f"Creating backup in: {backup_dir}")

        # Backup workspace info
        logger.info("Backing up workspace info...")
        workspace_info = slack.get_workspace_info()
        save_to_json(workspace_info, str(backup_dir / "workspace_info.json"))

        # Backup users
        logger.info("Backing up users...")
        users = slack.list_users(include_deleted=True)
        save_to_json(users, str(backup_dir / "users.json"))

        # Backup channels
        logger.info("Backing up channels...")
        channels = slack.list_channels(include_private=True, include_archived=True)
        save_to_json(channels, str(backup_dir / "channels.json"))

        # Backup files list
        logger.info("Backing up files list...")
        files = slack.list_files(count=1000)
        save_to_json(files, str(backup_dir / "files.json"))

        # Backup message history if requested
        if args.include_messages:
            logger.info(f"Backing up message history (up to {args.message_limit} per channel)...")
            messages_dir = backup_dir / "messages"
            ensure_directory(str(messages_dir))

            active_channels = [ch for ch in channels if not ch.get('is_archived')]

            for i, channel in enumerate(active_channels, 1):
                try:
                    logger.info(f"Backing up #{channel['name']} ({i}/{len(active_channels)})...")
                    messages = slack.get_channel_history(
                        channel['id'],
                        limit=args.message_limit
                    )

                    if messages:
                        channel_backup = {
                            'channel_id': channel['id'],
                            'channel_name': channel['name'],
                            'message_count': len(messages),
                            'messages': messages
                        }
                        save_to_json(
                            channel_backup,
                            str(messages_dir / f"{channel['name']}.json")
                        )
                except Exception as e:
                    logger.warning(f"Failed to backup #{channel['name']}: {e}")

        # Create backup manifest
        manifest = {
            'backup_date': datetime.now().isoformat(),
            'backup_type': 'full' if args.include_messages else 'metadata',
            'user_count': len(users),
            'channel_count': len(channels),
            'file_count': len(files),
            'includes_messages': args.include_messages
        }

        if args.include_messages:
            manifest['message_limit_per_channel'] = args.message_limit

        save_to_json(manifest, str(backup_dir / "manifest.json"))

        logger.info("\n" + "="*50)
        logger.info("✅ BACKUP COMPLETED")
        logger.info("="*50)
        logger.info(f"Location: {backup_dir}")
        logger.info(f"Users backed up: {len(users)}")
        logger.info(f"Channels backed up: {len(channels)}")
        logger.info(f"Files listed: {len(files)}")

        if args.include_messages:
            logger.info(f"Message history: Included (up to {args.message_limit} per channel)")
        else:
            logger.info(f"Message history: Not included (use --include-messages to include)")

        logger.info("="*50)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

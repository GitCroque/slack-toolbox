#!/usr/bin/env python3
"""
Find inactive channels (no messages in X days)
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
    parser = argparse.ArgumentParser(description='Find inactive Slack channels')
    parser.add_argument('--days', type=int, default=90,
                       help='Number of days of inactivity (default: 90)')
    parser.add_argument('--export', help='Export results to CSV file')
    parser.add_argument('--archive', action='store_true',
                       help='Archive inactive channels (use with caution!)')

    args = parser.parse_args()

    logger = setup_logger('find_inactive')

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get all active channels
        logger.info("Fetching channels...")
        channels = slack.list_channels(include_private=False, include_archived=False)
        logger.info(f"Found {len(channels)} active channels")

        # Calculate cutoff timestamp
        cutoff_ts = days_ago(args.days)

        # Check activity for each channel
        logger.info(f"Checking activity for last {args.days} days...")
        inactive_channels = []

        for i, channel in enumerate(channels, 1):
            if i % 10 == 0:
                logger.info(f"Processed {i}/{len(channels)} channels...")

            try:
                # Get recent messages
                messages = slack.get_channel_history(
                    channel['id'],
                    limit=1,
                    oldest=str(cutoff_ts)
                )

                # If no messages since cutoff, channel is inactive
                if not messages:
                    # Get last message to determine actual last activity
                    last_messages = slack.get_channel_history(channel['id'], limit=1)

                    last_activity = None
                    if last_messages:
                        last_ts = float(last_messages[0].get('ts', 0))
                        last_activity = datetime.fromtimestamp(last_ts).strftime('%Y-%m-%d')
                        days_inactive = int((datetime.now().timestamp() - last_ts) / 86400)
                    else:
                        days_inactive = 999

                    members = slack.get_channel_members(channel['id'])

                    inactive_channels.append({
                        'id': channel['id'],
                        'name': channel['name'],
                        'members': len(members),
                        'last_activity': last_activity or 'Never',
                        'days_inactive': days_inactive,
                        'topic': channel.get('topic', {}).get('value', '')[:50]
                    })

            except Exception as e:
                logger.warning(f"Error checking #{channel['name']}: {e}")

        # Sort by days inactive (descending)
        inactive_channels.sort(key=lambda x: x['days_inactive'], reverse=True)

        logger.info(f"\nFound {len(inactive_channels)} inactive channels")

        # Display results
        if inactive_channels:
            if args.export:
                save_to_csv(inactive_channels, args.export)
            else:
                headers = ['name', 'members', 'last_activity', 'days_inactive', 'topic']
                print_table(inactive_channels, headers=headers)

            # Archive if requested
            if args.archive:
                from lib.utils import confirm_action

                if confirm_action(f"Archive {len(inactive_channels)} inactive channels?", default=False):
                    archived_count = 0
                    for channel in inactive_channels:
                        try:
                            slack.archive_channel(channel['id'])
                            logger.info(f"Archived #{channel['name']}")
                            archived_count += 1
                        except Exception as e:
                            logger.error(f"Failed to archive #{channel['name']}: {e}")

                    logger.info(f"✅ Archived {archived_count} channels")
                else:
                    logger.info("Archive cancelled")
        else:
            print(f"No inactive channels found (no activity for {args.days}+ days)")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

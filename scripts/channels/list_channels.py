#!/usr/bin/env python3
"""
List all channels in the Slack workspace
"""

import argparse
import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import print_table, save_to_csv, save_to_json, format_timestamp
from lib.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(description='List all Slack channels')
    parser.add_argument('--include-private', action='store_true',
                       help='Include private channels')
    parser.add_argument('--include-archived', action='store_true',
                       help='Include archived channels')
    parser.add_argument('--export', choices=['csv', 'json'],
                       help='Export to file format')
    parser.add_argument('--output', help='Output filename for export')
    parser.add_argument('--with-members', action='store_true',
                       help='Include member count (slower)')

    args = parser.parse_args()

    logger = setup_logger('list_channels')

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get all channels
        logger.info("Fetching channels...")
        channels = slack.list_channels(
            include_private=args.include_private,
            include_archived=args.include_archived
        )

        logger.info(f"Found {len(channels)} channels")

        # Prepare data for display/export
        channel_data = []
        for channel in channels:
            # Determine channel type
            if channel.get('is_private'):
                ch_type = 'Private'
            else:
                ch_type = 'Public'

            # Status
            status = 'Archived' if channel.get('is_archived') else 'Active'

            channel_info = {
                'id': channel.get('id'),
                'name': channel.get('name'),
                'type': ch_type,
                'status': status,
                'topic': channel.get('topic', {}).get('value', '')[:50],
                'purpose': channel.get('purpose', {}).get('value', '')[:50],
                'created': format_timestamp(channel.get('created', 0)),
            }

            # Get member count if requested
            if args.with_members:
                members = slack.get_channel_members(channel['id'])
                channel_info['member_count'] = len(members)
            else:
                channel_info['member_count'] = channel.get('num_members', 0)

            channel_data.append(channel_info)

        # Sort by name
        channel_data.sort(key=lambda x: x['name'])

        # Export or display
        if args.export == 'csv':
            output_file = args.output or 'channels_export.csv'
            save_to_csv(channel_data, output_file)
        elif args.export == 'json':
            output_file = args.output or 'channels_export.json'
            save_to_json(channel_data, output_file)
        else:
            # Display as table
            headers = ['name', 'type', 'status', 'member_count', 'topic']
            print_table(channel_data, headers=headers)
            print(f"\nTotal: {len(channel_data)} channels")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

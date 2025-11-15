#!/usr/bin/env python3
"""
Export message history from a Slack channel
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import save_to_json, parse_timestamp, format_timestamp
from lib.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(description='Export Slack channel message history')
    parser.add_argument('--channel', required=True,
                       help='Channel name')
    parser.add_argument('--output', help='Output filename (JSON)')
    parser.add_argument('--limit', type=int, default=1000,
                       help='Maximum number of messages (default: 1000)')
    parser.add_argument('--after', help='Only messages after date (YYYY-MM-DD)')
    parser.add_argument('--before', help='Only messages before date (YYYY-MM-DD)')

    args = parser.parse_args()

    logger = setup_logger('export_channel_history')

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

        # Parse date filters
        oldest = parse_timestamp(args.after) if args.after else None
        latest = parse_timestamp(args.before) if args.before else None

        # Get message history
        logger.info(f"Fetching message history from #{args.channel}...")
        messages = slack.get_channel_history(
            channel_id,
            limit=args.limit,
            oldest=str(oldest) if oldest else None,
            latest=str(latest) if latest else None
        )

        logger.info(f"Retrieved {len(messages)} messages")

        # Format messages for export
        export_data = {
            'channel': {
                'id': channel_id,
                'name': args.channel,
                'export_date': datetime.now().isoformat()
            },
            'message_count': len(messages),
            'messages': []
        }

        # Get user info for better export
        users = slack.list_users()
        user_map = {u['id']: u for u in users}

        for msg in messages:
            user_id = msg.get('user')
            user = user_map.get(user_id, {})
            profile = user.get('profile', {})

            formatted_msg = {
                'timestamp': format_timestamp(float(msg.get('ts', 0))),
                'user_id': user_id,
                'user_name': user.get('name', 'unknown'),
                'user_display_name': profile.get('display_name') or profile.get('real_name', 'unknown'),
                'text': msg.get('text', ''),
                'type': msg.get('type', 'message'),
            }

            # Add thread info if present
            if msg.get('thread_ts'):
                formatted_msg['is_thread_reply'] = True
                formatted_msg['thread_ts'] = msg['thread_ts']

            # Add reactions if present
            if msg.get('reactions'):
                formatted_msg['reactions'] = msg['reactions']

            # Add files if present
            if msg.get('files'):
                formatted_msg['files'] = [
                    {
                        'name': f.get('name'),
                        'url': f.get('url_private'),
                        'size': f.get('size')
                    }
                    for f in msg['files']
                ]

            export_data['messages'].append(formatted_msg)

        # Generate output filename if not specified
        if not args.output:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            args.output = f"{args.channel}_history_{timestamp}.json"

        # Save to file
        save_to_json(export_data, args.output)
        logger.info(f"✅ Successfully exported {len(messages)} messages to {args.output}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

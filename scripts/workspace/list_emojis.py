#!/usr/bin/env python3
"""
List custom emojis in Slack workspace
"""

import sys
from pathlib import Path
import argparse

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import save_to_json, save_to_csv
from lib.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(description='List custom Slack emojis')
    parser.add_argument('--export', choices=['json', 'csv'],
                       help='Export emojis to file')
    parser.add_argument('--output', help='Output filename')

    args = parser.parse_args()

    logger = setup_logger('list_emojis')

    try:
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        logger.info("Fetching custom emojis...")
        response = slack.client.emoji_list()

        if not response['ok']:
            logger.error(f"Failed to fetch emojis: {response.get('error')}")
            sys.exit(1)

        emojis = response.get('emoji', {})

        logger.info(f"Found {len(emojis)} custom emojis")

        if not emojis:
            print("\nNo custom emojis found in this workspace")
            return

        # Display
        print(f"\n{'='*80}")
        print(f"CUSTOM EMOJIS ({len(emojis)})")
        print(f"{'='*80}\n")

        emoji_data = []

        for name, url in sorted(emojis.items()):
            print(f":{name}: → {url[:60]}...")

            emoji_data.append({
                'name': name,
                'url': url
            })

        print(f"\nTotal: {len(emojis)} custom emojis\n")

        # Export
        if args.export:
            output = args.output or f"custom_emojis.{args.export}"

            if args.export == 'json':
                save_to_json(emoji_data, output)
            else:
                save_to_csv(emoji_data, output)

            logger.info(f"✅ Exported to {output}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

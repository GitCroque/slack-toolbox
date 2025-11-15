#!/usr/bin/env python3
"""
Display statistics about Slack workspace users
"""

import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.logger import setup_logger


def main():
    logger = setup_logger('user_stats')

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get user statistics
        logger.info("Analyzing users...")
        stats = slack.get_user_stats()

        # Display statistics
        print("\n" + "="*50)
        print("SLACK WORKSPACE USER STATISTICS")
        print("="*50)
        print(f"\nTotal Users:        {stats['total']}")
        print(f"Active Users:       {stats['active']}")
        print(f"Deactivated Users:  {stats['deleted']}")
        print(f"Bot Users:          {stats['bots']}")
        print(f"\nAdministrators:     {stats['admins']}")
        print(f"Workspace Owners:   {stats['owners']}")
        print(f"Guest Users:        {stats['guests']}")
        print(f"Regular Members:    {stats['active'] - stats['admins'] - stats['owners'] - stats['guests']}")
        print("="*50 + "\n")

        # Calculate percentages
        if stats['total'] > 0:
            active_pct = (stats['active'] / stats['total']) * 100
            print(f"Active Rate: {active_pct:.1f}%")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

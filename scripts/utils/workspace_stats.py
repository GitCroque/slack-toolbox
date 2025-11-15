#!/usr/bin/env python3
"""
Display comprehensive workspace statistics
"""

import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.logger import setup_logger


def main():
    logger = setup_logger('workspace_stats')

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get workspace info
        logger.info("Gathering workspace statistics...")
        workspace_info = slack.get_workspace_info()
        team = workspace_info.get('team', {})

        # Get user statistics
        user_stats = slack.get_user_stats()

        # Get channel statistics
        channels = slack.list_channels(include_private=True, include_archived=False)
        archived_channels = slack.list_channels(include_private=True, include_archived=True)
        archived_count = len([ch for ch in archived_channels if ch.get('is_archived')])

        public_channels = [ch for ch in channels if not ch.get('is_private')]
        private_channels = [ch for ch in channels if ch.get('is_private')]

        # Display comprehensive stats
        print("\n" + "="*60)
        print("SLACK WORKSPACE STATISTICS")
        print("="*60)

        print(f"\n📊 WORKSPACE INFO")
        print(f"   Name:              {team.get('name', 'N/A')}")
        print(f"   Domain:            {team.get('domain', 'N/A')}")
        print(f"   Email Domain:      {team.get('email_domain', 'N/A')}")

        print(f"\n👥 USERS")
        print(f"   Total Users:       {user_stats['total']}")
        print(f"   Active Users:      {user_stats['active']}")
        print(f"   Deactivated:       {user_stats['deleted']}")
        print(f"   Bot Users:         {user_stats['bots']}")
        print(f"   ")
        print(f"   Workspace Owners:  {user_stats['owners']}")
        print(f"   Administrators:    {user_stats['admins']}")
        print(f"   Guest Users:       {user_stats['guests']}")
        print(f"   Regular Members:   {user_stats['active'] - user_stats['admins'] - user_stats['owners'] - user_stats['guests']}")

        print(f"\n📢 CHANNELS")
        print(f"   Total Active:      {len(channels)}")
        print(f"   Public Channels:   {len(public_channels)}")
        print(f"   Private Channels:  {len(private_channels)}")
        print(f"   Archived:          {archived_count}")

        # Calculate average members per channel
        if channels:
            avg_members = sum(ch.get('num_members', 0) for ch in channels) / len(channels)
            print(f"   Avg Members/Channel: {avg_members:.1f}")

        # Find most popular channels
        popular_channels = sorted(public_channels, key=lambda x: x.get('num_members', 0), reverse=True)[:5]
        if popular_channels:
            print(f"\n🔥 MOST POPULAR PUBLIC CHANNELS")
            for i, ch in enumerate(popular_channels, 1):
                print(f"   {i}. #{ch['name']}: {ch.get('num_members', 0)} members")

        # Calculate percentages
        if user_stats['total'] > 0:
            active_pct = (user_stats['active'] / user_stats['total']) * 100
            guest_pct = (user_stats['guests'] / user_stats['total']) * 100
            print(f"\n📈 METRICS")
            print(f"   Active User Rate:  {active_pct:.1f}%")
            print(f"   Guest Percentage:  {guest_pct:.1f}%")

        print("="*60 + "\n")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

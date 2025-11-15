#!/usr/bin/env python3
"""
Generate advanced activity report for Slack workspace
Shows most active users, popular channels, file sharing stats, etc.
"""

import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import argparse

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import days_ago, save_to_json, format_bytes
from lib.logger import setup_logger


def generate_activity_report(slack, days, logger):
    """Generate comprehensive activity report"""

    cutoff_ts = days_ago(days)

    report = {
        'generated_at': datetime.now().isoformat(),
        'period_days': days,
        'workspace_stats': {},
        'channel_activity': [],
        'file_stats': {},
        'top_channels': [],
        'recommendations': []
    }

    # Workspace stats
    logger.info("Gathering workspace statistics...")
    workspace_info = slack.get_workspace_info()
    user_stats = slack.get_user_stats()

    report['workspace_stats'] = {
        'workspace_name': workspace_info.get('team', {}).get('name', 'Unknown'),
        'total_users': user_stats['total'],
        'active_users': user_stats['active'],
        'admins': user_stats['admins'],
        'guests': user_stats['guests']
    }

    # Channel activity
    logger.info("Analyzing channel activity...")
    channels = slack.list_channels(include_private=False, include_archived=False)

    channel_stats = []
    total_messages = 0

    for channel in channels[:20]:  # Limit to first 20 for performance
        try:
            # Get recent messages
            messages = slack.get_channel_history(
                channel['id'],
                oldest=str(cutoff_ts),
                limit=1000
            )

            message_count = len(messages)
            total_messages += message_count

            if message_count > 0:
                # Count unique participants
                participants = set()
                for msg in messages:
                    if msg.get('user'):
                        participants.add(msg['user'])

                channel_stats.append({
                    'name': channel['name'],
                    'messages': message_count,
                    'participants': len(participants),
                    'members': channel.get('num_members', 0)
                })
        except Exception as e:
            logger.warning(f"Error analyzing #{channel['name']}: {e}")

    # Sort by activity
    channel_stats.sort(key=lambda x: x['messages'], reverse=True)
    report['channel_activity'] = channel_stats
    report['top_channels'] = channel_stats[:10]

    # File statistics
    logger.info("Analyzing file sharing...")
    files = slack.list_files(count=1000)

    file_stats = {
        'total_files': len(files),
        'total_size': sum(f.get('size', 0) for f in files),
        'total_size_formatted': format_bytes(sum(f.get('size', 0) for f in files))
    }

    # Count by type
    file_types = defaultdict(int)
    for f in files:
        ftype = f.get('filetype', 'unknown')
        file_types[ftype] += 1

    file_stats['by_type'] = dict(file_types)
    report['file_stats'] = file_stats

    # Generate recommendations
    if user_stats['guests'] > user_stats['active'] * 0.3:
        report['recommendations'].append({
            'type': 'security',
            'message': f"High percentage of guest users ({user_stats['guests']}). Review guest permissions."
        })

    inactive_channels = [ch for ch in channel_stats if ch['messages'] == 0]
    if len(inactive_channels) > 5:
        report['recommendations'].append({
            'type': 'cleanup',
            'message': f"{len(inactive_channels)} channels with no activity. Consider archiving."
        })

    if file_stats['total_size'] > 5 * 1024 * 1024 * 1024:  # 5GB
        report['recommendations'].append({
            'type': 'storage',
            'message': f"Large file storage: {file_stats['total_size_formatted']}. Review old files."
        })

    return report


def print_report(report):
    """Print formatted report"""

    print(f"\n{'='*80}")
    print("SLACK WORKSPACE ACTIVITY REPORT")
    print(f"{'='*80}\n")

    print(f"Generated: {report['generated_at']}")
    print(f"Period: Last {report['period_days']} days\n")

    # Workspace stats
    ws = report['workspace_stats']
    print(f"{'='*80}")
    print("WORKSPACE OVERVIEW")
    print(f"{'='*80}")
    print(f"Workspace: {ws['workspace_name']}")
    print(f"Total Users: {ws['total_users']}")
    print(f"Active Users: {ws['active_users']}")
    print(f"Administrators: {ws['admins']}")
    print(f"Guest Users: {ws['guests']}\n")

    # Top channels
    if report['top_channels']:
        print(f"{'='*80}")
        print(f"TOP {len(report['top_channels'])} MOST ACTIVE CHANNELS")
        print(f"{'='*80}")
        for i, ch in enumerate(report['top_channels'], 1):
            print(f"{i:2}. #{ch['name']:<20} "
                  f"Messages: {ch['messages']:4}  "
                  f"Participants: {ch['participants']:3}  "
                  f"Members: {ch['members']:3}")
        print()

    # File stats
    fs = report['file_stats']
    print(f"{'='*80}")
    print("FILE SHARING STATISTICS")
    print(f"{'='*80}")
    print(f"Total Files: {fs['total_files']}")
    print(f"Total Size: {fs['total_size_formatted']}")

    if fs.get('by_type'):
        print(f"\nTop file types:")
        sorted_types = sorted(fs['by_type'].items(), key=lambda x: x[1], reverse=True)
        for ftype, count in sorted_types[:5]:
            print(f"  - {ftype}: {count}")
    print()

    # Recommendations
    if report['recommendations']:
        print(f"{'='*80}")
        print(f"RECOMMENDATIONS ({len(report['recommendations'])})")
        print(f"{'='*80}")
        for rec in report['recommendations']:
            icon = {'security': '🔒', 'cleanup': '🧹', 'storage': '💾'}.get(rec['type'], '💡')
            print(f"{icon} [{rec['type'].upper()}] {rec['message']}")
        print()

    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description='Generate activity report')
    parser.add_argument('--days', type=int, default=30,
                       help='Number of days to analyze (default: 30)')
    parser.add_argument('--output', help='Save report to JSON file')

    args = parser.parse_args()

    logger = setup_logger('activity_report')

    try:
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        print(f"\n🔍 Generating activity report for last {args.days} days...")
        print("This may take a few minutes...\n")

        report = generate_activity_report(slack, args.days, logger)

        # Print report
        print_report(report)

        # Save if requested
        if args.output:
            save_to_json(report, args.output)
            logger.info(f"✅ Report saved to {args.output}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

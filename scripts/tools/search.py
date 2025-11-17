#!/usr/bin/env python3
"""
Universal search tool for Slack workspace
Search users, channels, messages, files, etc.
"""

import argparse
import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import print_table, get_user_display_name
from lib.logger import setup_logger


def search_users(slack, query, logger):
    """Search users by name, email, or ID"""
    logger.info("Searching users...")

    users = slack.list_users()
    query_lower = query.lower()

    results = []

    for user in users:
        # Skip bots unless specifically searching for them
        if user.get('is_bot'):
            continue

        profile = user.get('profile', {})

        # Search in multiple fields
        matches = []

        if query_lower in user.get('name', '').lower():
            matches.append('username')

        if query_lower in profile.get('email', '').lower():
            matches.append('email')

        if query_lower in profile.get('real_name', '').lower():
            matches.append('real_name')

        if query_lower in profile.get('display_name', '').lower():
            matches.append('display_name')

        if query_lower in user.get('id', '').lower():
            matches.append('id')

        if matches:
            results.append({
                'type': 'User',
                'name': user.get('name'),
                'display_name': get_user_display_name(user),
                'email': profile.get('email', ''),
                'id': user.get('id'),
                'match': ', '.join(matches),
                'status': 'Deactivated' if user.get('deleted') else 'Active'
            })

    return results


def search_channels(slack, query, logger):
    """Search channels by name or topic"""
    logger.info("Searching channels...")

    channels = slack.list_channels(include_private=True, include_archived=True)
    query_lower = query.lower()

    results = []

    for channel in channels:
        matches = []

        if query_lower in channel.get('name', '').lower():
            matches.append('name')

        topic = channel.get('topic', {}).get('value', '')
        if query_lower in topic.lower():
            matches.append('topic')

        purpose = channel.get('purpose', {}).get('value', '')
        if query_lower in purpose.lower():
            matches.append('purpose')

        if query_lower in channel.get('id', '').lower():
            matches.append('id')

        if matches:
            ch_type = 'Private' if channel.get('is_private') else 'Public'
            status = 'Archived' if channel.get('is_archived') else 'Active'

            results.append({
                'type': 'Channel',
                'name': f"#{channel.get('name')}",
                'display_name': topic[:50] if topic else purpose[:50],
                'email': '',  # For consistent table format
                'id': channel.get('id'),
                'match': ', '.join(matches),
                'status': f"{ch_type}, {status}"
            })

    return results


def search_files(slack, query, logger):
    """Search files by name"""
    logger.info("Searching files...")

    files = slack.list_files(count=1000)
    query_lower = query.lower()

    results = []

    for file in files:
        matches = []

        if query_lower in file.get('name', '').lower():
            matches.append('filename')

        if query_lower in file.get('title', '').lower():
            matches.append('title')

        if matches:
            # Get user who uploaded
            users = slack.list_users()
            user_map = {u['id']: u for u in users}
            user = user_map.get(file.get('user'), {})
            user_name = user.get('name', 'Unknown')

            results.append({
                'type': 'File',
                'name': file.get('name', 'Unnamed'),
                'display_name': file.get('title', '')[:50],
                'email': user_name,
                'id': file.get('id'),
                'match': ', '.join(matches),
                'status': f"{file.get('size', 0)} bytes"
            })

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Universal search for Slack workspace',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search everything
  python3 search.py --query john

  # Search only users
  python3 search.py --query john --type user

  # Search by email domain
  python3 search.py --query @example.com --type user

  # Search channels
  python3 search.py --query engineering --type channel

  # Search multiple types
  python3 search.py --query project --type user,channel

Search types:
  - user: Search users (name, email, display name)
  - channel: Search channels (name, topic, purpose)
  - file: Search files (filename, title)
  - all: Search everything (default)
        """
    )

    parser.add_argument('--query', '-q', required=True,
                       help='Search query')
    parser.add_argument('--type', '-t', default='all',
                       help='Search type: user, channel, file, or all (default: all)')
    parser.add_argument('--limit', type=int, default=50,
                       help='Maximum results to display (default: 50)')
    parser.add_argument('--case-sensitive', action='store_true',
                       help='Case sensitive search')

    args = parser.parse_args()

    logger = setup_logger('search')

    # Parse search types
    if args.type == 'all':
        search_types = ['user', 'channel', 'file']
    else:
        search_types = [t.strip() for t in args.type.split(',')]

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        print(f"\n{'='*80}")
        print(f"SEARCHING: '{args.query}'")
        print(f"Types: {', '.join(search_types)}")
        print(f"{'='*80}\n")

        all_results = []

        # Search each type
        if 'user' in search_types:
            results = search_users(slack, args.query, logger)
            all_results.extend(results)
            logger.info(f"Found {len(results)} users")

        if 'channel' in search_types:
            results = search_channels(slack, args.query, logger)
            all_results.extend(results)
            logger.info(f"Found {len(results)} channels")

        if 'file' in search_types:
            results = search_files(slack, args.query, logger)
            all_results.extend(results)
            logger.info(f"Found {len(results)} files")

        # Display results
        if not all_results:
            print("❌ No results found\n")
            sys.exit(0)

        # Limit results
        if len(all_results) > args.limit:
            print(f"⚠️  Showing first {args.limit} of {len(all_results)} results\n")
            all_results = all_results[:args.limit]

        # Print results table
        headers = ['type', 'name', 'display_name', 'match', 'status', 'id']
        print_table(all_results, headers=headers, max_width=40)

        print(f"\n✅ Found {len(all_results)} results")

        # Summary by type
        type_counts = {}
        for result in all_results:
            result_type = result['type']
            type_counts[result_type] = type_counts.get(result_type, 0) + 1

        if len(type_counts) > 1:
            print("\nBreakdown:")
            for result_type, count in sorted(type_counts.items()):
                print(f"  - {result_type}s: {count}")

        print()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Find duplicate or similar users in Slack workspace
Detects potential duplicate accounts, similar names, etc.
"""

import sys
from pathlib import Path
from difflib import SequenceMatcher

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import print_table, save_to_csv
from lib.logger import setup_logger
import argparse


def similar(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_duplicates(slack, logger, similarity_threshold=0.85):
    """Find duplicate or similar users"""

    logger.info("Fetching users...")
    users = slack.list_users()

    # Filter out bots and deleted
    active_users = [u for u in users if not u.get('is_bot') and not u.get('deleted')]

    logger.info(f"Analyzing {len(active_users)} active users...")

    duplicates = []

    # Check for duplicate emails (shouldn't happen but let's check)
    email_map = {}
    for user in active_users:
        profile = user.get('profile', {})
        email = profile.get('email', '').lower()

        if email:
            if email in email_map:
                duplicates.append({
                    'type': 'Duplicate Email',
                    'user1': email_map[email].get('name'),
                    'user2': user.get('name'),
                    'field': 'email',
                    'value': email,
                    'similarity': 1.0
                })
            else:
                email_map[email] = user

    # Check for similar names
    for i, user1 in enumerate(active_users):
        profile1 = user1.get('profile', {})
        name1 = profile1.get('real_name', user1.get('name', ''))

        for user2 in active_users[i+1:]:
            profile2 = user2.get('profile', {})
            name2 = profile2.get('real_name', user2.get('name', ''))

            # Calculate similarity
            sim = similar(name1, name2)

            if sim >= similarity_threshold and sim < 1.0:
                duplicates.append({
                    'type': 'Similar Name',
                    'user1': user1.get('name'),
                    'user2': user2.get('name'),
                    'field': 'real_name',
                    'value': f"{name1} / {name2}",
                    'similarity': sim
                })

    return duplicates


def main():
    parser = argparse.ArgumentParser(description='Find duplicate or similar users')
    parser.add_argument('--similarity', type=float, default=0.85,
                       help='Similarity threshold (0.0-1.0, default: 0.85)')
    parser.add_argument('--export', help='Export results to CSV')

    args = parser.parse_args()

    logger = setup_logger('find_duplicates')

    try:
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        print(f"\n{'='*60}")
        print("DUPLICATE DETECTION")
        print(f"{'='*60}\n")

        duplicates = find_duplicates(slack, logger, args.similarity)

        if not duplicates:
            print("✅ No duplicates found!")
            print()
            return

        print(f"⚠️  Found {len(duplicates)} potential duplicates:\n")

        # Display results
        headers = ['type', 'user1', 'user2', 'field', 'similarity']
        display_data = []

        for dup in duplicates:
            display_data.append({
                'type': dup['type'],
                'user1': dup['user1'],
                'user2': dup['user2'],
                'field': dup['field'],
                'similarity': f"{dup['similarity']:.2%}"
            })

        print_table(display_data, headers=headers)

        # Export if requested
        if args.export:
            save_to_csv(duplicates, args.export)
            print(f"\n✅ Results exported to {args.export}")

        print()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

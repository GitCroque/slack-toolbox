#!/usr/bin/env python3
"""
Audit user permissions and roles in Slack workspace
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.utils import save_to_csv, print_table, get_user_display_name
from lib.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(description='Audit Slack user permissions')
    parser.add_argument('--export', help='Export to CSV file')
    parser.add_argument('--role', choices=['admin', 'owner', 'guest'],
                       help='Filter by specific role')

    args = parser.parse_args()

    logger = setup_logger('permissions_audit')

    try:
        # Initialize Slack client
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get all users
        logger.info("Fetching users and analyzing permissions...")
        users = slack.list_users()

        # Analyze permissions
        audit_data = []

        for user in users:
            # Skip bots
            if user.get('is_bot'):
                continue

            profile = user.get('profile', {})

            # Determine all roles/permissions
            roles = []
            if user.get('is_owner'):
                roles.append('Owner')
            if user.get('is_admin'):
                roles.append('Admin')
            if user.get('is_primary_owner'):
                roles.append('Primary Owner')
            if user.get('is_restricted'):
                roles.append('Multi-Channel Guest')
            if user.get('is_ultra_restricted'):
                roles.append('Single-Channel Guest')
            if not roles:
                roles.append('Member')

            # Check 2FA status
            has_2fa = user.get('has_2fa', False)

            user_info = {
                'id': user['id'],
                'name': user.get('name'),
                'email': profile.get('email', ''),
                'display_name': get_user_display_name(user),
                'roles': ', '.join(roles),
                'is_owner': user.get('is_owner', False),
                'is_admin': user.get('is_admin', False),
                'is_guest': user.get('is_restricted', False) or user.get('is_ultra_restricted', False),
                'has_2fa': has_2fa,
                'status': 'Deactivated' if user.get('deleted') else 'Active'
            }

            # Filter by role if specified
            if args.role:
                if args.role == 'admin' and not user.get('is_admin'):
                    continue
                elif args.role == 'owner' and not user.get('is_owner'):
                    continue
                elif args.role == 'guest' and not (user.get('is_restricted') or user.get('is_ultra_restricted')):
                    continue

            audit_data.append(user_info)

        # Sort by role importance (owners, admins, guests, members)
        def role_sort_key(u):
            if u['is_owner']:
                return 0
            elif u['is_admin']:
                return 1
            elif u['is_guest']:
                return 2
            else:
                return 3

        audit_data.sort(key=role_sort_key)

        logger.info(f"Analyzed {len(audit_data)} users")

        # Display or export
        if args.export:
            save_to_csv(audit_data, args.export)
        else:
            headers = ['name', 'email', 'roles', 'has_2fa', 'status']
            print_table(audit_data, headers=headers)

            # Summary statistics
            total = len(audit_data)
            owners = sum(1 for u in audit_data if u['is_owner'])
            admins = sum(1 for u in audit_data if u['is_admin'])
            guests = sum(1 for u in audit_data if u['is_guest'])
            with_2fa = sum(1 for u in audit_data if u['has_2fa'])

            print("\n" + "="*50)
            print("PERMISSION AUDIT SUMMARY")
            print("="*50)
            print(f"Total Users:      {total}")
            print(f"Owners:           {owners}")
            print(f"Admins:           {admins}")
            print(f"Guests:           {guests}")
            print(f"With 2FA:         {with_2fa} ({(with_2fa/total*100):.1f}%)")
            print(f"Without 2FA:      {total-with_2fa} ({((total-with_2fa)/total*100):.1f}%)")
            print("="*50)

            if total - with_2fa > 0:
                print("\n⚠️  Warning: Some users don't have 2FA enabled!")
                print("   Consider enforcing 2FA for better security.")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

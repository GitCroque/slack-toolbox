#!/usr/bin/env python3
"""
List all users in the Slack workspace with details
"""

import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.script_base import SlackScript
from lib.utils import print_table, save_to_csv, save_to_json, get_user_display_name


class ListUsersScript(SlackScript):
    """Script to list all Slack users with filtering and export options"""

    def setup_arguments(self, parser):
        """Add script-specific arguments"""
        parser.add_argument('--include-deleted', action='store_true',
                           help='Include deactivated users')
        parser.add_argument('--include-bots', action='store_true',
                           help='Include bot users')
        parser.add_argument('--role', choices=['admin', 'owner', 'member', 'guest'],
                           help='Filter by role')
        parser.add_argument('--export', choices=['csv', 'json'],
                           help='Export to file format')
        parser.add_argument('--output', help='Output filename for export')
        parser.add_argument('--verbose', action='store_true',
                           help='Show detailed information')

    def execute(self):
        """Main script logic"""
        # Get all users
        self.logger.info("Fetching users...")
        users = self.slack.list_users(include_deleted=self.args.include_deleted)

        # Filter users
        filtered_users = self._filter_users(users)
        self.logger.info(f"Found {len(filtered_users)} users")

        # Prepare data for display/export
        user_data = self._prepare_user_data(filtered_users)

        # Export or display
        if self.args.export == 'csv':
            output_file = self.args.output or 'users_export.csv'
            if not self.dry_run_check(f"Export {len(user_data)} users to {output_file}"):
                save_to_csv(user_data, output_file)
        elif self.args.export == 'json':
            output_file = self.args.output or 'users_export.json'
            if not self.dry_run_check(f"Export {len(user_data)} users to {output_file}"):
                save_to_json(user_data, output_file)
        else:
            # Display as table
            headers = ['name', 'display_name', 'email', 'role', 'status']
            if self.args.verbose:
                headers.extend(['title', 'timezone'])

            print_table(user_data, headers=headers)
            print(f"\nTotal: {len(user_data)} users")

    def _filter_users(self, users):
        """Filter users based on arguments"""
        filtered = []

        for user in users:
            # Skip bots unless requested
            if user.get('is_bot') and not self.args.include_bots:
                continue

            # Filter by role
            if self.args.role:
                if self.args.role == 'admin' and not user.get('is_admin'):
                    continue
                elif self.args.role == 'owner' and not user.get('is_owner'):
                    continue
                elif self.args.role == 'guest' and not (user.get('is_restricted') or user.get('is_ultra_restricted')):
                    continue
                elif self.args.role == 'member' and (user.get('is_admin') or user.get('is_owner') or
                                                     user.get('is_restricted') or user.get('is_ultra_restricted')):
                    continue

            filtered.append(user)

        return filtered

    def _prepare_user_data(self, users):
        """Prepare user data for display/export"""
        user_data = []

        for user in users:
            profile = user.get('profile', {})

            # Determine role
            if user.get('is_owner'):
                role = 'Owner'
            elif user.get('is_admin'):
                role = 'Admin'
            elif user.get('is_ultra_restricted'):
                role = 'Single-Channel Guest'
            elif user.get('is_restricted'):
                role = 'Multi-Channel Guest'
            else:
                role = 'Member'

            # Determine status
            if user.get('deleted'):
                status = 'Deactivated'
            elif user.get('is_bot'):
                status = 'Bot'
            else:
                status = 'Active'

            user_info = {
                'id': user.get('id'),
                'name': user.get('name'),
                'display_name': get_user_display_name(user),
                'real_name': profile.get('real_name', ''),
                'email': profile.get('email', ''),
                'role': role,
                'status': status,
                'timezone': user.get('tz_label', ''),
            }

            if self.args.verbose:
                user_info.update({
                    'title': profile.get('title', ''),
                    'phone': profile.get('phone', ''),
                    'updated': user.get('updated', ''),
                })

            user_data.append(user_info)

        return user_data


if __name__ == '__main__':
    script = ListUsersScript(
        name='list_users',
        description='List all Slack users with filtering and export options'
    )
    sys.exit(script.run())

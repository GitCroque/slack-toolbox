#!/usr/bin/env python3
"""
Compare two Slack workspace backups and show differences
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from difflib import unified_diff

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.logger import setup_logger
from lib.utils import save_to_csv, save_to_json


class BackupComparator:
    """Compare two backup directories and identify changes"""

    def __init__(self, backup1_path: str, backup2_path: str, logger):
        """
        Initialize comparator

        Args:
            backup1_path: Path to first (older) backup
            backup2_path: Path to second (newer) backup
            logger: Logger instance
        """
        self.backup1 = Path(backup1_path)
        self.backup2 = Path(backup2_path)
        self.logger = logger

        if not self.backup1.exists():
            raise FileNotFoundError(f"Backup not found: {backup1_path}")
        if not self.backup2.exists():
            raise FileNotFoundError(f"Backup not found: {backup2_path}")

    def _load_json_file(self, backup_path: Path, filename: str) -> Dict:
        """Load JSON file from backup"""
        file_path = backup_path / filename

        if not file_path.exists():
            self.logger.warning(f"File not found: {file_path}")
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load {file_path}: {e}")
            return {}

    def compare_users(self) -> Dict:
        """Compare users between backups"""
        users1 = self._load_json_file(self.backup1, 'users.json')
        users2 = self._load_json_file(self.backup2, 'users.json')

        users1_dict = {u['id']: u for u in users1.get('members', [])}
        users2_dict = {u['id']: u for u in users2.get('members', [])}

        ids1 = set(users1_dict.keys())
        ids2 = set(users2_dict.keys())

        added = ids2 - ids1
        removed = ids1 - ids2
        common = ids1 & ids2

        # Check for changes in existing users
        modified = []
        for user_id in common:
            user1 = users1_dict[user_id]
            user2 = users2_dict[user_id]

            changes = {}

            # Check status changes
            if user1.get('deleted') != user2.get('deleted'):
                changes['deleted'] = {
                    'old': user1.get('deleted'),
                    'new': user2.get('deleted')
                }

            # Check admin status
            if user1.get('is_admin') != user2.get('is_admin'):
                changes['is_admin'] = {
                    'old': user1.get('is_admin'),
                    'new': user2.get('is_admin')
                }

            # Check owner status
            if user1.get('is_owner') != user2.get('is_owner'):
                changes['is_owner'] = {
                    'old': user1.get('is_owner'),
                    'new': user2.get('is_owner')
                }

            # Check profile changes
            profile1 = user1.get('profile', {})
            profile2 = user2.get('profile', {})

            if profile1.get('title') != profile2.get('title'):
                changes['title'] = {
                    'old': profile1.get('title'),
                    'new': profile2.get('title')
                }

            if profile1.get('real_name') != profile2.get('real_name'):
                changes['real_name'] = {
                    'old': profile1.get('real_name'),
                    'new': profile2.get('real_name')
                }

            if changes:
                modified.append({
                    'id': user_id,
                    'name': user2.get('name'),
                    'real_name': profile2.get('real_name'),
                    'changes': changes
                })

        return {
            'added': [users2_dict[uid] for uid in added],
            'removed': [users1_dict[uid] for uid in removed],
            'modified': modified,
            'stats': {
                'total_before': len(users1_dict),
                'total_after': len(users2_dict),
                'added_count': len(added),
                'removed_count': len(removed),
                'modified_count': len(modified)
            }
        }

    def compare_channels(self) -> Dict:
        """Compare channels between backups"""
        channels1 = self._load_json_file(self.backup1, 'channels.json')
        channels2 = self._load_json_file(self.backup2, 'channels.json')

        channels1_dict = {c['id']: c for c in channels1.get('channels', [])}
        channels2_dict = {c['id']: c for c in channels2.get('channels', [])}

        ids1 = set(channels1_dict.keys())
        ids2 = set(channels2_dict.keys())

        added = ids2 - ids1
        removed = ids1 - ids2
        common = ids1 & ids2

        # Check for changes
        modified = []
        for channel_id in common:
            ch1 = channels1_dict[channel_id]
            ch2 = channels2_dict[channel_id]

            changes = {}

            # Check archive status
            if ch1.get('is_archived') != ch2.get('is_archived'):
                changes['is_archived'] = {
                    'old': ch1.get('is_archived'),
                    'new': ch2.get('is_archived')
                }

            # Check name
            if ch1.get('name') != ch2.get('name'):
                changes['name'] = {
                    'old': ch1.get('name'),
                    'new': ch2.get('name')
                }

            # Check topic
            if ch1.get('topic', {}).get('value') != ch2.get('topic', {}).get('value'):
                changes['topic'] = {
                    'old': ch1.get('topic', {}).get('value'),
                    'new': ch2.get('topic', {}).get('value')
                }

            # Check purpose
            if ch1.get('purpose', {}).get('value') != ch2.get('purpose', {}).get('value'):
                changes['purpose'] = {
                    'old': ch1.get('purpose', {}).get('value'),
                    'new': ch2.get('purpose', {}).get('value')
                }

            # Check member count
            members1 = ch1.get('num_members', 0)
            members2 = ch2.get('num_members', 0)
            if members1 != members2:
                changes['num_members'] = {
                    'old': members1,
                    'new': members2,
                    'diff': members2 - members1
                }

            if changes:
                modified.append({
                    'id': channel_id,
                    'name': ch2.get('name'),
                    'changes': changes
                })

        return {
            'added': [channels2_dict[cid] for cid in added],
            'removed': [channels1_dict[cid] for cid in removed],
            'modified': modified,
            'stats': {
                'total_before': len(channels1_dict),
                'total_after': len(channels2_dict),
                'added_count': len(added),
                'removed_count': len(removed),
                'modified_count': len(modified)
            }
        }

    def compare_files(self) -> Dict:
        """Compare file metadata between backups"""
        files1 = self._load_json_file(self.backup1, 'files_metadata.json')
        files2 = self._load_json_file(self.backup2, 'files_metadata.json')

        files1_list = files1.get('files', [])
        files2_list = files2.get('files', [])

        # Compare file counts and sizes
        total_size1 = sum(f.get('size', 0) for f in files1_list)
        total_size2 = sum(f.get('size', 0) for f in files2_list)

        return {
            'stats': {
                'count_before': len(files1_list),
                'count_after': len(files2_list),
                'count_diff': len(files2_list) - len(files1_list),
                'size_before': total_size1,
                'size_after': total_size2,
                'size_diff': total_size2 - total_size1
            }
        }

    def generate_report(self) -> Dict:
        """Generate complete comparison report"""
        self.logger.info("Comparing backups...")
        self.logger.info(f"  Backup 1: {self.backup1}")
        self.logger.info(f"  Backup 2: {self.backup2}")

        report = {
            'comparison_date': datetime.now().isoformat(),
            'backup1_path': str(self.backup1),
            'backup2_path': str(self.backup2),
            'users': self.compare_users(),
            'channels': self.compare_channels(),
            'files': self.compare_files()
        }

        return report

    def print_report(self, report: Dict):
        """Print human-readable comparison report"""
        print("\n" + "=" * 80)
        print("BACKUP COMPARISON REPORT".center(80))
        print("=" * 80)

        print(f"\nBackup 1: {report['backup1_path']}")
        print(f"Backup 2: {report['backup2_path']}")
        print(f"Comparison Date: {report['comparison_date']}")

        # Users section
        print("\n" + "-" * 80)
        print("USERS")
        print("-" * 80)

        users = report['users']
        stats = users['stats']

        print(f"\nTotal Users: {stats['total_before']} → {stats['total_after']}")
        print(f"  Added: {stats['added_count']}")
        print(f"  Removed: {stats['removed_count']}")
        print(f"  Modified: {stats['modified_count']}")

        if users['added']:
            print(f"\n✅ Added Users ({len(users['added'])}):")
            for user in users['added'][:10]:  # Show first 10
                profile = user.get('profile', {})
                print(f"  • {user.get('name')} - {profile.get('real_name')} ({profile.get('email')})")
            if len(users['added']) > 10:
                print(f"  ... and {len(users['added']) - 10} more")

        if users['removed']:
            print(f"\n❌ Removed Users ({len(users['removed'])}):")
            for user in users['removed'][:10]:
                profile = user.get('profile', {})
                print(f"  • {user.get('name')} - {profile.get('real_name')}")
            if len(users['removed']) > 10:
                print(f"  ... and {len(users['removed']) - 10} more")

        if users['modified']:
            print(f"\n🔄 Modified Users ({len(users['modified'])}):")
            for user in users['modified'][:10]:
                print(f"  • {user['name']} - {user.get('real_name')}")
                for field, change in user['changes'].items():
                    print(f"    - {field}: {change['old']} → {change['new']}")
            if len(users['modified']) > 10:
                print(f"  ... and {len(users['modified']) - 10} more")

        # Channels section
        print("\n" + "-" * 80)
        print("CHANNELS")
        print("-" * 80)

        channels = report['channels']
        stats = channels['stats']

        print(f"\nTotal Channels: {stats['total_before']} → {stats['total_after']}")
        print(f"  Added: {stats['added_count']}")
        print(f"  Removed: {stats['removed_count']}")
        print(f"  Modified: {stats['modified_count']}")

        if channels['added']:
            print(f"\n✅ Added Channels ({len(channels['added'])}):")
            for channel in channels['added'][:10]:
                print(f"  • #{channel.get('name')}")
            if len(channels['added']) > 10:
                print(f"  ... and {len(channels['added']) - 10} more")

        if channels['removed']:
            print(f"\n❌ Removed Channels ({len(channels['removed'])}):")
            for channel in channels['removed'][:10]:
                print(f"  • #{channel.get('name')}")
            if len(channels['removed']) > 10:
                print(f"  ... and {len(channels['removed']) - 10} more")

        if channels['modified']:
            print(f"\n🔄 Modified Channels ({len(channels['modified'])}):")
            for channel in channels['modified'][:10]:
                print(f"  • #{channel['name']}")
                for field, change in channel['changes'].items():
                    if field == 'num_members':
                        diff = change['diff']
                        sign = '+' if diff > 0 else ''
                        print(f"    - {field}: {change['old']} → {change['new']} ({sign}{diff})")
                    else:
                        print(f"    - {field}: {change['old']} → {change['new']}")
            if len(channels['modified']) > 10:
                print(f"  ... and {len(channels['modified']) - 10} more")

        # Files section
        print("\n" + "-" * 80)
        print("FILES")
        print("-" * 80)

        files = report['files']['stats']
        print(f"\nTotal Files: {files['count_before']} → {files['count_after']}")
        print(f"  Difference: {files['count_diff']:+d}")
        print(f"\nTotal Storage: {self._format_bytes(files['size_before'])} → {self._format_bytes(files['size_after'])}")
        print(f"  Difference: {self._format_bytes(files['size_diff'], signed=True)}")

        print("\n" + "=" * 80)

    def _format_bytes(self, size: int, signed: bool = False) -> str:
        """Format bytes to human readable"""
        sign = ''
        if signed and size > 0:
            sign = '+'
        elif size < 0:
            sign = '-'
            size = abs(size)

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{sign}{size:.2f} {unit}"
            size /= 1024.0
        return f"{sign}{size:.2f} PB"


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Compare two Slack workspace backups',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare two backup directories
  python compare_backups.py backups/2024-01-01_backup backups/2024-01-15_backup

  # Export comparison to JSON
  python compare_backups.py backup1 backup2 --format json --output comparison.json

  # Export to CSV (separate files for users, channels)
  python compare_backups.py backup1 backup2 --format csv --output comparison
        """
    )

    parser.add_argument('backup1', help='Path to first (older) backup')
    parser.add_argument('backup2', help='Path to second (newer) backup')
    parser.add_argument('--format', choices=['json', 'csv', 'text'], default='text',
                        help='Output format (default: text)')
    parser.add_argument('--output', help='Output file path (for json/csv formats)')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level')

    args = parser.parse_args()

    # Setup logger
    logger = setup_logger('compare_backups', level=args.log_level)

    try:
        # Create comparator
        comparator = BackupComparator(args.backup1, args.backup2, logger)

        # Generate report
        report = comparator.generate_report()

        # Output based on format
        if args.format == 'text':
            comparator.print_report(report)

        elif args.format == 'json':
            output_file = args.output or 'backup_comparison.json'
            save_to_json(report, output_file)
            logger.info(f"✅ Comparison saved to: {output_file}")

        elif args.format == 'csv':
            base_name = args.output or 'backup_comparison'

            # Export users changes
            if report['users']['added'] or report['users']['removed'] or report['users']['modified']:
                users_data = []

                # Added users
                for user in report['users']['added']:
                    profile = user.get('profile', {})
                    users_data.append({
                        'change_type': 'added',
                        'user_id': user.get('id'),
                        'username': user.get('name'),
                        'real_name': profile.get('real_name'),
                        'email': profile.get('email'),
                        'changes': ''
                    })

                # Removed users
                for user in report['users']['removed']:
                    profile = user.get('profile', {})
                    users_data.append({
                        'change_type': 'removed',
                        'user_id': user.get('id'),
                        'username': user.get('name'),
                        'real_name': profile.get('real_name'),
                        'email': profile.get('email'),
                        'changes': ''
                    })

                # Modified users
                for user in report['users']['modified']:
                    changes_str = ', '.join([f"{k}: {v['old']}→{v['new']}" for k, v in user['changes'].items()])
                    users_data.append({
                        'change_type': 'modified',
                        'user_id': user['id'],
                        'username': user['name'],
                        'real_name': user.get('real_name', ''),
                        'email': '',
                        'changes': changes_str
                    })

                users_file = f"{base_name}_users.csv"
                save_to_csv(users_data, users_file)
                logger.info(f"✅ Users comparison saved to: {users_file}")

            # Export channels changes
            if report['channels']['added'] or report['channels']['removed'] or report['channels']['modified']:
                channels_data = []

                # Added channels
                for channel in report['channels']['added']:
                    channels_data.append({
                        'change_type': 'added',
                        'channel_id': channel.get('id'),
                        'name': channel.get('name'),
                        'is_archived': channel.get('is_archived'),
                        'changes': ''
                    })

                # Removed channels
                for channel in report['channels']['removed']:
                    channels_data.append({
                        'change_type': 'removed',
                        'channel_id': channel.get('id'),
                        'name': channel.get('name'),
                        'is_archived': channel.get('is_archived'),
                        'changes': ''
                    })

                # Modified channels
                for channel in report['channels']['modified']:
                    changes_str = ', '.join([f"{k}: {v['old']}→{v['new']}" for k, v in channel['changes'].items()])
                    channels_data.append({
                        'change_type': 'modified',
                        'channel_id': channel['id'],
                        'name': channel['name'],
                        'is_archived': '',
                        'changes': changes_str
                    })

                channels_file = f"{base_name}_channels.csv"
                save_to_csv(channels_data, channels_file)
                logger.info(f"✅ Channels comparison saved to: {channels_file}")

        logger.info("\n✅ Backup comparison complete!")

    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Comparison failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()

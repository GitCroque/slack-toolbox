#!/usr/bin/env python3
"""
Export reports to PDF format
"""

import argparse
import sys
from pathlib import Path
import json

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.pdf_generator import (
    generate_user_report_pdf,
    generate_audit_report_pdf,
    generate_activity_report_pdf
)
from lib.utils import get_user_display_name
from lib.logger import setup_logger


def export_users_pdf(slack, output_file, logger):
    """Export users to PDF"""
    logger.info("Fetching users...")
    users = slack.list_users()

    # Prepare data
    users_data = []
    for user in users:
        if user.get('is_bot'):
            continue

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

        users_data.append({
            'display_name': get_user_display_name(user),
            'email': profile.get('email', ''),
            'role': role,
            'status': 'Deactivated' if user.get('deleted') else 'Active'
        })

    # Generate PDF
    logger.info(f"Generating PDF with {len(users_data)} users...")
    generate_user_report_pdf(users_data, output_file)
    logger.info(f"✅ PDF generated: {output_file}")


def export_audit_pdf(slack, output_file, logger):
    """Export audit report to PDF"""
    logger.info("Running security audit...")

    users = slack.list_users()

    # Prepare audit data
    stats = {
        'total': len(users),
        'active': 0,
        'admins': 0,
        'owners': 0,
        'with_2fa': 0,
        'guests': 0
    }

    security_issues = []

    for user in users:
        if user.get('deleted') or user.get('is_bot'):
            continue

        stats['active'] += 1

        if user.get('is_admin'):
            stats['admins'] += 1

        if user.get('is_owner'):
            stats['owners'] += 1

        if user.get('is_restricted') or user.get('is_ultra_restricted'):
            stats['guests'] += 1

        if user.get('has_2fa'):
            stats['with_2fa'] += 1
        else:
            # Security issue: admin without 2FA
            if user.get('is_admin') or user.get('is_owner'):
                profile = user.get('profile', {})
                security_issues.append({
                    'severity': 'HIGH',
                    'type': 'Admin without 2FA',
                    'user': user['name'],
                    'email': profile.get('email', 'N/A')
                })

    # Recommendations
    recommendations = []
    if stats['with_2fa'] < stats['active'] * 0.5:
        recommendations.append("Enable 2FA requirement for all users")

    if stats['guests'] > stats['active'] * 0.3:
        recommendations.append(f"High guest percentage ({stats['guests']}). Review guest permissions.")

    audit_data = {
        'workspace_stats': {
            'Total Users': stats['total'],
            'Active Users': stats['active'],
            'Administrators': stats['admins'],
            'Owners': stats['owners'],
            'Guests': stats['guests'],
            'Users with 2FA': stats['with_2fa'],
            '2FA Coverage': f"{stats['with_2fa']/stats['active']*100:.1f}%" if stats['active'] > 0 else '0%'
        },
        'security_issues': security_issues,
        'recommendations': recommendations
    }

    # Generate PDF
    logger.info(f"Generating audit PDF...")
    generate_audit_report_pdf(audit_data, output_file)
    logger.info(f"✅ Audit PDF generated: {output_file}")


def export_activity_pdf(slack, output_file, days, logger):
    """Export activity report to PDF"""
    from lib.utils import days_ago
    from collections import defaultdict

    logger.info(f"Generating activity report for last {days} days...")

    cutoff_ts = days_ago(days)

    # Get workspace info
    workspace_info = slack.get_workspace_info()
    user_stats = slack.get_user_stats()

    # Get channels
    channels = slack.list_channels(include_private=False, include_archived=False)

    channel_stats = []
    for channel in channels[:20]:  # Limit for performance
        try:
            messages = slack.get_channel_history(
                channel['id'],
                oldest=str(cutoff_ts),
                limit=1000
            )

            if len(messages) > 0:
                participants = set()
                for msg in messages:
                    if msg.get('user'):
                        participants.add(msg['user'])

                channel_stats.append({
                    'name': channel['name'],
                    'messages': len(messages),
                    'participants': len(participants),
                    'members': channel.get('num_members', 0)
                })
        except Exception as e:
            logger.warning(f"Error analyzing #{channel['name']}: {e}")

    channel_stats.sort(key=lambda x: x['messages'], reverse=True)

    # Get file stats
    files = slack.list_files(count=1000)
    file_types = defaultdict(int)
    total_size = 0

    for f in files:
        ftype = f.get('filetype', 'unknown')
        file_types[ftype] += 1
        total_size += f.get('size', 0)

    # Format bytes
    def format_bytes(bytes_size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"

    activity_data = {
        'workspace_stats': {
            'Workspace': workspace_info.get('team', {}).get('name', 'Unknown'),
            'Total Users': user_stats['total'],
            'Active Users': user_stats['active'],
            'Administrators': user_stats['admins'],
            'Active Channels': len(channels),
            'Report Period': f'{days} days'
        },
        'top_channels': channel_stats[:10],
        'file_stats': {
            'total_files': len(files),
            'total_size_formatted': format_bytes(total_size)
        }
    }

    # Generate PDF
    logger.info("Generating activity PDF...")
    generate_activity_report_pdf(activity_data, output_file)
    logger.info(f"✅ Activity PDF generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Export Slack reports to PDF')
    parser.add_argument('--type', required=True, choices=['users', 'audit', 'activity'],
                       help='Type of report to generate')
    parser.add_argument('--output', help='Output PDF filename')
    parser.add_argument('--days', type=int, default=30,
                       help='Number of days for activity report (default: 30)')

    args = parser.parse_args()

    logger = setup_logger('export_pdf')

    try:
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Generate output filename if not specified
        if not args.output:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            args.output = f"slack_{args.type}_report_{timestamp}.pdf"

        # Generate appropriate report
        if args.type == 'users':
            export_users_pdf(slack, args.output, logger)
        elif args.type == 'audit':
            export_audit_pdf(slack, args.output, logger)
        elif args.type == 'activity':
            export_activity_pdf(slack, args.output, args.days, logger)

        print(f"\n✅ PDF report generated: {args.output}\n")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

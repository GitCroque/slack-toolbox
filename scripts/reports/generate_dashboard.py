#!/usr/bin/env python3
"""
Generate HTML dashboard with Slack workspace statistics
"""

import sys
from pathlib import Path
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.logger import setup_logger


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slack Workspace Dashboard - {workspace_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            text-align: center;
        }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        .timestamp {{ color: #666; font-size: 14px; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .card h2 {{
            font-size: 18px;
            color: #555;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        .stat {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        .stat:last-child {{ border-bottom: none; }}
        .stat-label {{ color: #666; }}
        .stat-value {{
            font-weight: bold;
            color: #333;
            font-size: 18px;
        }}
        .big-number {{
            font-size: 48px;
            font-weight: bold;
            color: #667eea;
            text-align: center;
            margin: 20px 0;
        }}
        .channel-list {{
            list-style: none;
            max-height: 300px;
            overflow-y: auto;
        }}
        .channel-list li {{
            padding: 8px 0;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
        }}
        .channel-name {{ color: #667eea; font-weight: 500; }}
        .channel-members {{ color: #999; font-size: 14px; }}
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }}
        .footer a {{ color: white; text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Slack Workspace Dashboard</h1>
            <h2>{workspace_name}</h2>
            <p class="timestamp">Generated: {timestamp}</p>
        </div>

        <div class="grid">
            <div class="card">
                <h2>👥 Users</h2>
                <div class="big-number">{total_users}</div>
                <div class="stat">
                    <span class="stat-label">Active:</span>
                    <span class="stat-value">{active_users}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Deactivated:</span>
                    <span class="stat-value">{deleted_users}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Bots:</span>
                    <span class="stat-value">{bots}</span>
                </div>
            </div>

            <div class="card">
                <h2>🔐 Roles</h2>
                <div class="stat">
                    <span class="stat-label">Owners:</span>
                    <span class="stat-value">{owners}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Admins:</span>
                    <span class="stat-value">{admins}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Guests:</span>
                    <span class="stat-value">{guests}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Members:</span>
                    <span class="stat-value">{members}</span>
                </div>
            </div>

            <div class="card">
                <h2>📢 Channels</h2>
                <div class="big-number">{total_channels}</div>
                <div class="stat">
                    <span class="stat-label">Public:</span>
                    <span class="stat-value">{public_channels}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Private:</span>
                    <span class="stat-value">{private_channels}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Archived:</span>
                    <span class="stat-value">{archived_channels}</span>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🔥 Top Public Channels</h2>
            <ul class="channel-list">
                {channel_list}
            </ul>
        </div>

        <div class="footer">
            <p>Generated by <a href="https://github.com/GitCroque/slack-script">Slack Management Platform</a></p>
        </div>
    </div>
</body>
</html>
"""


def generate_dashboard(output_file='dashboard.html'):
    """Generate HTML dashboard"""

    logger = setup_logger('generate_dashboard')

    try:
        slack = SlackManager()
        logger.info("Connected to Slack workspace")

        # Get workspace info
        workspace_info = slack.get_workspace_info()
        workspace_name = workspace_info.get('team', {}).get('name', 'Unknown Workspace')

        # Get user stats
        user_stats = slack.get_user_stats()

        # Get channels
        channels = slack.list_channels(include_private=True, include_archived=False)
        all_channels = slack.list_channels(include_private=True, include_archived=True)

        public_channels = [ch for ch in channels if not ch.get('is_private')]
        private_channels = [ch for ch in channels if ch.get('is_private')]
        archived_channels = [ch for ch in all_channels if ch.get('is_archived')]

        # Sort public channels by members
        top_channels = sorted(public_channels, key=lambda x: x.get('num_members', 0), reverse=True)[:10]

        # Generate channel list HTML
        channel_list_html = ''
        for ch in top_channels:
            channel_list_html += f'''
                <li>
                    <span class="channel-name">#{ch['name']}</span>
                    <span class="channel-members">{ch.get('num_members', 0)} members</span>
                </li>
            '''

        # Calculate members
        members = user_stats['active'] - user_stats['admins'] - user_stats['owners'] - user_stats['guests']

        # Fill template
        html = HTML_TEMPLATE.format(
            workspace_name=workspace_name,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_users=user_stats['total'],
            active_users=user_stats['active'],
            deleted_users=user_stats['deleted'],
            bots=user_stats['bots'],
            owners=user_stats['owners'],
            admins=user_stats['admins'],
            guests=user_stats['guests'],
            members=members,
            total_channels=len(channels),
            public_channels=len(public_channels),
            private_channels=len(private_channels),
            archived_channels=len(archived_channels),
            channel_list=channel_list_html
        )

        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"✅ Dashboard generated: {output_file}")
        print(f"\n✅ Dashboard generated: {output_file}")
        print(f"   Open it in your browser to view\n")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate HTML dashboard')
    parser.add_argument('--output', default='dashboard.html',
                       help='Output filename (default: dashboard.html)')

    args = parser.parse_args()

    generate_dashboard(args.output)

#!/usr/bin/env python3
"""
Send notifications via Slack webhook
"""

import argparse
import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.notifier import SlackWebhookNotifier
from lib.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(
        description='Send Slack webhook notifications',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple message
  python3 send_notification.py --webhook https://hooks.slack.com/... --message "Backup completed"

  # Success notification
  python3 send_notification.py --webhook https://hooks.slack.com/... --type success --title "Backup Done" --message "All files backed up successfully"

  # Warning notification
  python3 send_notification.py --webhook https://hooks.slack.com/... --type warning --title "Low Space" --message "Disk space running low"

  # Error notification
  python3 send_notification.py --webhook https://hooks.slack.com/... --type error --title "Backup Failed" --message "Error during backup process"

Get webhook URL:
  1. Go to https://api.slack.com/apps
  2. Select your app (or create one)
  3. Incoming Webhooks → Activate → Add New Webhook to Workspace
  4. Copy the webhook URL
        """
    )

    parser.add_argument('--webhook', required=True,
                       help='Slack webhook URL')
    parser.add_argument('--message', required=True,
                       help='Notification message')
    parser.add_argument('--title', help='Notification title (for rich messages)')
    parser.add_argument('--type', choices=['simple', 'success', 'warning', 'error'],
                       default='simple',
                       help='Notification type (default: simple)')
    parser.add_argument('--fields', nargs='*',
                       help='Additional fields (format: "Key:Value")')

    args = parser.parse_args()

    logger = setup_logger('send_notification')

    try:
        notifier = SlackWebhookNotifier(args.webhook)

        # Parse fields if provided
        fields = None
        if args.fields:
            fields = []
            for field in args.fields:
                if ':' in field:
                    key, value = field.split(':', 1)
                    fields.append({
                        'title': key.strip(),
                        'value': value.strip(),
                        'short': True
                    })

        # Send notification based on type
        if args.type == 'simple':
            success = notifier.send(args.message)
        elif args.type == 'success':
            title = args.title or "✅ Success"
            success = notifier.send_success(title, args.message, fields=fields)
        elif args.type == 'warning':
            title = args.title or "⚠️ Warning"
            success = notifier.send_warning(title, args.message, fields=fields)
        elif args.type == 'error':
            title = args.title or "❌ Error"
            success = notifier.send_error(title, args.message, fields=fields)
        else:
            success = False

        if success:
            logger.info("✅ Notification sent successfully")
        else:
            logger.error("❌ Failed to send notification")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

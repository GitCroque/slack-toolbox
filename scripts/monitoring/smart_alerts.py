#!/usr/bin/env python3
"""
Smart alerting system - detect anomalies and send notifications
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.logger import setup_logger
from lib.alerts import AlertDetector, AlertManager, Alert
from lib.notifier import SlackWebhookNotifier, MultiNotifier
from lib.utils import load_config


def collect_workspace_data(slack: SlackManager, logger) -> dict:
    """
    Collect all workspace data for analysis

    Args:
        slack: SlackManager instance
        logger: Logger instance

    Returns:
        Dict with users, channels, files
    """
    logger.info("Collecting workspace data...")

    data = {
        'users': [],
        'channels': [],
        'files': []
    }

    try:
        # Get users
        logger.info("  Fetching users...")
        result = slack.client.users_list()
        if result.get('ok'):
            data['users'] = result.get('members', [])
            logger.info(f"    Found {len(data['users'])} users")

        # Get channels
        logger.info("  Fetching channels...")
        result = slack.client.conversations_list(
            types='public_channel,private_channel',
            limit=1000
        )
        if result.get('ok'):
            data['channels'] = result.get('channels', [])
            logger.info(f"    Found {len(data['channels'])} channels")

        # Get files (metadata only)
        logger.info("  Fetching file metadata...")
        result = slack.client.files_list(count=1000)
        if result.get('ok'):
            data['files'] = result.get('files', [])
            logger.info(f"    Found {len(data['files'])} files")

    except Exception as e:
        logger.error(f"Error collecting data: {e}")

    return data


def load_previous_data(data_file: Path) -> dict:
    """
    Load previous workspace data for comparison

    Args:
        data_file: Path to previous data JSON file

    Returns:
        Previous data dict or None
    """
    if not data_file.exists():
        return None

    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def save_workspace_data(data: dict, data_file: Path):
    """
    Save workspace data for future comparison

    Args:
        data: Workspace data dict
        data_file: Path to save data
    """
    data_file.parent.mkdir(parents=True, exist_ok=True)

    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def print_alerts(alerts: list, logger):
    """
    Print alerts to console

    Args:
        alerts: List of Alert objects
        logger: Logger instance
    """
    if not alerts:
        logger.info("✅ No alerts detected - workspace looks healthy!")
        return

    logger.info(f"\n{'=' * 80}")
    logger.info(f"ALERTS DETECTED: {len(alerts)}")
    logger.info(f"{'=' * 80}\n")

    # Group by severity
    critical = [a for a in alerts if a.severity == Alert.SEVERITY_CRITICAL]
    warning = [a for a in alerts if a.severity == Alert.SEVERITY_WARNING]
    info = [a for a in alerts if a.severity == Alert.SEVERITY_INFO]

    if critical:
        logger.critical(f"\n🚨 CRITICAL ALERTS ({len(critical)}):")
        for alert in critical:
            logger.critical(f"\n  {alert.title}")
            logger.critical(f"  {alert.message}")
            if alert.details:
                logger.critical(f"  Details: {json.dumps(alert.details, indent=4)}")

    if warning:
        logger.warning(f"\n⚠️  WARNING ALERTS ({len(warning)}):")
        for alert in warning:
            logger.warning(f"\n  {alert.title}")
            logger.warning(f"  {alert.message}")
            if alert.details:
                logger.warning(f"  Details: {json.dumps(alert.details, indent=4)}")

    if info:
        logger.info(f"\nℹ️  INFO ALERTS ({len(info)}):")
        for alert in info:
            logger.info(f"\n  {alert.title}")
            logger.info(f"  {alert.message}")

    logger.info(f"\n{'=' * 80}\n")


def send_notifications(alerts: list, config: dict, logger):
    """
    Send alert notifications via configured channels

    Args:
        alerts: List of Alert objects
        config: Configuration dict
        logger: Logger instance
    """
    webhook_url = config.get('webhook_url')

    if not webhook_url:
        logger.warning("No webhook URL configured - skipping notifications")
        return

    logger.info("Sending notifications...")

    notifier = SlackWebhookNotifier(webhook_url)

    # Group by severity
    critical = [a for a in alerts if a.severity == Alert.SEVERITY_CRITICAL]
    warning = [a for a in alerts if a.severity == Alert.SEVERITY_WARNING]
    info = [a for a in alerts if a.severity == Alert.SEVERITY_INFO]

    # Send critical alerts
    if critical:
        for alert in critical[:5]:  # Send first 5 critical
            fields = []
            if 'count' in alert.details or 'percentage' in alert.details:
                for key, value in alert.details.items():
                    if key not in ['users', 'channels', 'changes']:  # Skip large data
                        fields.append({
                            'title': key.replace('_', ' ').title(),
                            'value': str(value),
                            'short': True
                        })

            notifier.send_error(
                alert.title,
                alert.message,
                fields=fields if fields else None
            )

    # Send summary for warnings and info
    if warning or info:
        summary_message = f"*Warnings:* {len(warning)}\n*Info:* {len(info)}"

        if warning:
            summary_message += "\n\n*Top Warnings:*\n"
            for alert in warning[:3]:
                summary_message += f"• {alert.title}\n"

        notifier.send_warning(
            "Workspace Alerts Summary",
            summary_message
        )

    logger.info("✅ Notifications sent")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Smart alerting system for Slack workspace',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run alert checks
  python smart_alerts.py

  # Save alerts to file
  python smart_alerts.py --output alerts.json

  # Send notifications via webhook
  python smart_alerts.py --notify

  # Use custom thresholds
  python smart_alerts.py --inactive-days 60 --storage-warning 50

  # Compare with previous snapshot
  python smart_alerts.py --compare
        """
    )

    parser.add_argument('--config', default='config/config.json',
                        help='Path to config file')
    parser.add_argument('--output', help='Save alerts to JSON file')
    parser.add_argument('--notify', action='store_true',
                        help='Send notifications via configured channels')
    parser.add_argument('--compare', action='store_true',
                        help='Compare with previous snapshot')
    parser.add_argument('--data-file', default='data/workspace_snapshot.json',
                        help='Path to store workspace snapshot for comparison')

    # Threshold overrides
    parser.add_argument('--inactive-days', type=int,
                        help='Days threshold for inactive users')
    parser.add_argument('--inactive-percentage', type=int,
                        help='Percentage threshold for inactive users alert')
    parser.add_argument('--storage-warning', type=int,
                        help='Storage warning threshold (GB)')
    parser.add_argument('--storage-critical', type=int,
                        help='Storage critical threshold (GB)')
    parser.add_argument('--deactivation-spike', type=int,
                        help='Threshold for deactivation spike alert')

    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level')

    args = parser.parse_args()

    # Setup logger
    logger = setup_logger('smart_alerts', level=args.log_level)

    try:
        # Load config
        config = load_config(args.config)

        # Apply threshold overrides
        threshold_config = {}
        if args.inactive_days:
            threshold_config['inactive_user_threshold'] = args.inactive_days
        if args.inactive_percentage:
            threshold_config['inactive_user_percentage'] = args.inactive_percentage
        if args.storage_warning:
            threshold_config['storage_warning_gb'] = args.storage_warning
        if args.storage_critical:
            threshold_config['storage_critical_gb'] = args.storage_critical
        if args.deactivation_spike:
            threshold_config['deactivation_spike'] = args.deactivation_spike

        # Merge with config
        config.update(threshold_config)

        # Initialize Slack client
        logger.info("Initializing Slack client...")
        slack = SlackManager(config_path=args.config)

        # Collect current workspace data
        current_data = collect_workspace_data(slack, logger)

        # Load previous data if comparison requested
        previous_data = None
        if args.compare:
            logger.info("Loading previous snapshot for comparison...")
            previous_data = load_previous_data(Path(args.data_file))
            if previous_data:
                logger.info("  Previous snapshot loaded")
            else:
                logger.warning("  No previous snapshot found - running without comparison")

        # Initialize alert detector
        logger.info("\nRunning alert checks...")
        detector = AlertDetector(config=config)

        # Run all checks
        alerts = detector.run_all_checks(current_data, previous_data)

        # Create alert manager
        alert_manager = AlertManager()
        alert_manager.add_alerts(alerts)

        # Print alerts to console
        print_alerts(alerts, logger)

        # Save alerts if requested
        if args.output:
            output_path = Path(args.output)
            alert_manager.alert_file = output_path
            alert_manager.save()
            logger.info(f"✅ Alerts saved to: {output_path}")

        # Send notifications if requested
        if args.notify and alerts:
            send_notifications(alerts, config, logger)

        # Save current data as snapshot for next comparison
        if args.compare:
            save_workspace_data(current_data, Path(args.data_file))
            logger.info(f"✅ Workspace snapshot saved to: {args.data_file}")

        # Summary
        summary = alert_manager.get_summary()
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Alerts: {summary['total']}")
        logger.info(f"  Critical: {summary['critical']}")
        logger.info(f"  Warning: {summary['warning']}")
        logger.info(f"  Info: {summary['info']}")

        if summary['by_type']:
            logger.info("\nAlerts by Type:")
            for alert_type, count in summary['by_type'].items():
                logger.info(f"  {alert_type}: {count}")

        logger.info("=" * 80)

        # Exit with non-zero if critical alerts
        if summary['critical'] > 0:
            logger.warning("\n⚠️  Critical alerts detected - please review immediately!")
            sys.exit(2)
        elif summary['warning'] > 0:
            logger.info("\n✅ Scan complete with warnings")
            sys.exit(1)
        else:
            logger.info("\n✅ Scan complete - no issues detected!")
            sys.exit(0)

    except Exception as e:
        logger.error(f"❌ Smart alerts failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()

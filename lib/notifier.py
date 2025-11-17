#!/usr/bin/env python3
"""
Notification system for Slack Management Platform
Supports Slack webhooks, email, and more
"""

import requests
import json
from datetime import datetime
from typing import Optional, Dict, List


class SlackWebhookNotifier:
    """Send notifications via Slack incoming webhooks"""

    def __init__(self, webhook_url: str):
        """
        Initialize notifier with webhook URL

        Args:
            webhook_url: Slack incoming webhook URL
        """
        self.webhook_url = webhook_url

    def send(self, message: str, **kwargs) -> bool:
        """
        Send a simple text message

        Args:
            message: Message text
            **kwargs: Additional message properties

        Returns:
            True if successful
        """
        payload = {
            'text': message,
            **kwargs
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False

    def send_rich(self, title: str, message: str, color='good', fields: Optional[List[Dict]] = None) -> bool:
        """
        Send a rich formatted message with attachments

        Args:
            title: Message title
            message: Message text
            color: Message color (good, warning, danger, or hex)
            fields: Additional fields to display

        Returns:
            True if successful
        """
        attachment = {
            'title': title,
            'text': message,
            'color': color,
            'ts': int(datetime.now().timestamp())
        }

        if fields:
            attachment['fields'] = fields

        payload = {
            'attachments': [attachment]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send rich notification: {e}")
            return False

    def send_success(self, title: str, message: str, **kwargs) -> bool:
        """Send success notification (green)"""
        return self.send_rich(title, message, color='good', **kwargs)

    def send_warning(self, title: str, message: str, **kwargs) -> bool:
        """Send warning notification (yellow)"""
        return self.send_rich(title, message, color='warning', **kwargs)

    def send_error(self, title: str, message: str, **kwargs) -> bool:
        """Send error notification (red)"""
        return self.send_rich(title, message, color='danger', **kwargs)

    def send_backup_notification(self, backup_path: str, file_count: int, success: bool = True):
        """Send backup completion notification"""
        if success:
            return self.send_success(
                "✅ Backup Completed",
                f"Workspace backup successful\nLocation: `{backup_path}`\nFiles: {file_count}",
                fields=[
                    {'title': 'Status', 'value': 'Success', 'short': True},
                    {'title': 'Time', 'value': datetime.now().strftime('%Y-%m-%d %H:%M'), 'short': True}
                ]
            )
        else:
            return self.send_error(
                "❌ Backup Failed",
                f"Workspace backup failed\nPlease check logs for details"
            )

    def send_audit_alert(self, issues_found: int, critical_count: int = 0):
        """Send audit alert notification"""
        if issues_found == 0:
            return self.send_success(
                "✅ Security Audit Complete",
                "No security issues found"
            )
        else:
            color = 'danger' if critical_count > 0 else 'warning'
            return self.send_rich(
                "⚠️ Security Audit Alert",
                f"Found {issues_found} security issues\nCritical: {critical_count}",
                color=color,
                fields=[
                    {'title': 'Total Issues', 'value': str(issues_found), 'short': True},
                    {'title': 'Critical', 'value': str(critical_count), 'short': True}
                ]
            )

    def send_inactive_users_alert(self, inactive_count: int, threshold_days: int):
        """Send inactive users alert"""
        if inactive_count == 0:
            return self.send_success(
                "✅ User Activity Check",
                f"All users active within {threshold_days} days"
            )
        else:
            return self.send_warning(
                "⚠️ Inactive Users Detected",
                f"Found {inactive_count} users inactive for {threshold_days}+ days",
                fields=[
                    {'title': 'Inactive Users', 'value': str(inactive_count), 'short': True},
                    {'title': 'Threshold', 'value': f'{threshold_days} days', 'short': True}
                ]
            )


class EmailNotifier:
    """Send notifications via email"""

    def __init__(self, smtp_config: Dict):
        """
        Initialize email notifier

        Args:
            smtp_config: SMTP configuration dict with host, port, user, password, from_addr
        """
        self.config = smtp_config

    def send(self, to: str, subject: str, body: str) -> bool:
        """
        Send email notification

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body

        Returns:
            True if successful
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.get('from_addr')
            msg['To'] = to
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.config.get('host'), self.config.get('port')) as server:
                if self.config.get('use_tls'):
                    server.starttls()

                if self.config.get('user') and self.config.get('password'):
                    server.login(self.config.get('user'), self.config.get('password'))

                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False


class MultiNotifier:
    """Send notifications to multiple channels"""

    def __init__(self):
        self.notifiers = []

    def add_slack_webhook(self, webhook_url: str):
        """Add Slack webhook notifier"""
        self.notifiers.append(('slack', SlackWebhookNotifier(webhook_url)))

    def add_email(self, smtp_config: Dict):
        """Add email notifier"""
        self.notifiers.append(('email', EmailNotifier(smtp_config)))

    def send(self, message: str, **kwargs):
        """Send notification to all configured channels"""
        results = []

        for notifier_type, notifier in self.notifiers:
            try:
                if notifier_type == 'slack':
                    result = notifier.send(message, **kwargs)
                elif notifier_type == 'email' and 'to' in kwargs and 'subject' in kwargs:
                    result = notifier.send(kwargs['to'], kwargs['subject'], message)
                else:
                    result = False

                results.append((notifier_type, result))
            except Exception as e:
                print(f"Error sending via {notifier_type}: {e}")
                results.append((notifier_type, False))

        return results

#!/usr/bin/env python3
"""
Intelligent alerting system for Slack workspace
Detects anomalies, thresholds, and unusual patterns
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class Alert:
    """Represents a single alert"""

    SEVERITY_INFO = 'info'
    SEVERITY_WARNING = 'warning'
    SEVERITY_CRITICAL = 'critical'

    def __init__(self, alert_type: str, severity: str, title: str, message: str, details: Dict = None):
        """
        Initialize alert

        Args:
            alert_type: Type of alert (user_activity, permissions, storage, etc.)
            severity: Severity level (info, warning, critical)
            title: Alert title
            message: Alert message
            details: Additional details dict
        """
        self.alert_type = alert_type
        self.severity = severity
        self.title = title
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        """Convert alert to dict"""
        return {
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

    def __repr__(self):
        return f"Alert({self.severity.upper()}: {self.title})"


class AlertDetector:
    """Detect various anomalies and threshold violations"""

    def __init__(self, config: Dict = None):
        """
        Initialize detector with configuration

        Args:
            config: Configuration dict with thresholds and settings
        """
        self.config = config or {}
        self.alerts = []

        # Default thresholds
        self.thresholds = {
            'inactive_user_days': self.config.get('inactive_user_threshold', 90),
            'inactive_user_percentage': self.config.get('inactive_user_percentage', 30),
            'storage_warning_gb': self.config.get('storage_warning_gb', 80),
            'storage_critical_gb': self.config.get('storage_critical_gb', 95),
            'deactivation_spike_count': self.config.get('deactivation_spike', 5),
            'admin_change_spike': self.config.get('admin_change_spike', 3),
            'channel_archive_spike': self.config.get('channel_archive_spike', 10),
            'guest_account_percentage': self.config.get('guest_percentage', 20),
            'external_sharing_count': self.config.get('external_sharing_limit', 50)
        }

    def check_inactive_users(self, users: List[Dict]) -> List[Alert]:
        """
        Check for inactive users

        Args:
            users: List of user dicts from Slack API

        Returns:
            List of alerts
        """
        alerts = []
        now = datetime.now()
        threshold_days = self.thresholds['inactive_user_days']
        threshold_date = now - timedelta(days=threshold_days)

        inactive_users = []

        for user in users:
            if user.get('deleted') or user.get('is_bot'):
                continue

            # Check last activity (approximation using updated field)
            updated = user.get('updated', 0)
            if updated:
                last_activity = datetime.fromtimestamp(updated)
                if last_activity < threshold_date:
                    inactive_users.append({
                        'id': user.get('id'),
                        'name': user.get('name'),
                        'real_name': user.get('profile', {}).get('real_name'),
                        'last_activity': last_activity.strftime('%Y-%m-%d'),
                        'days_inactive': (now - last_activity).days
                    })

        if inactive_users:
            total_users = len([u for u in users if not u.get('deleted') and not u.get('is_bot')])
            inactive_percentage = (len(inactive_users) / total_users * 100) if total_users > 0 else 0

            severity = Alert.SEVERITY_CRITICAL if inactive_percentage > self.thresholds['inactive_user_percentage'] else Alert.SEVERITY_WARNING

            alerts.append(Alert(
                alert_type='user_activity',
                severity=severity,
                title=f'Inactive Users Detected',
                message=f'Found {len(inactive_users)} users inactive for {threshold_days}+ days ({inactive_percentage:.1f}% of workspace)',
                details={
                    'inactive_count': len(inactive_users),
                    'total_users': total_users,
                    'percentage': round(inactive_percentage, 2),
                    'threshold_days': threshold_days,
                    'users': inactive_users[:20]  # Include first 20
                }
            ))

        return alerts

    def check_recent_deactivations(self, users: List[Dict], days: int = 7) -> List[Alert]:
        """
        Check for unusual spike in user deactivations

        Args:
            users: List of user dicts
            days: Number of days to check for spike

        Returns:
            List of alerts
        """
        alerts = []
        now = datetime.now()
        cutoff_date = now - timedelta(days=days)

        recent_deactivations = []

        for user in users:
            if not user.get('deleted'):
                continue

            # Check when deleted (approximation)
            updated = user.get('updated', 0)
            if updated:
                deactivation_date = datetime.fromtimestamp(updated)
                if deactivation_date >= cutoff_date:
                    recent_deactivations.append({
                        'id': user.get('id'),
                        'name': user.get('name'),
                        'real_name': user.get('profile', {}).get('real_name'),
                        'date': deactivation_date.strftime('%Y-%m-%d')
                    })

        if len(recent_deactivations) >= self.thresholds['deactivation_spike_count']:
            alerts.append(Alert(
                alert_type='user_deactivation',
                severity=Alert.SEVERITY_CRITICAL,
                title='Unusual Deactivation Spike',
                message=f'{len(recent_deactivations)} users deactivated in the last {days} days',
                details={
                    'deactivation_count': len(recent_deactivations),
                    'days': days,
                    'users': recent_deactivations
                }
            ))

        return alerts

    def check_admin_changes(self, users: List[Dict], previous_users: List[Dict] = None) -> List[Alert]:
        """
        Check for unusual admin/owner permission changes

        Args:
            users: Current user list
            previous_users: Previous user list for comparison

        Returns:
            List of alerts
        """
        alerts = []

        # Count current admins and owners
        admin_count = len([u for u in users if u.get('is_admin') and not u.get('deleted')])
        owner_count = len([u for u in users if u.get('is_owner') and not u.get('deleted')])

        # Alert if no owners (critical issue)
        if owner_count == 0:
            alerts.append(Alert(
                alert_type='permissions',
                severity=Alert.SEVERITY_CRITICAL,
                title='No Workspace Owners',
                message='No active workspace owners detected - this is a critical security issue',
                details={'owner_count': 0}
            ))

        # Alert if only one owner (warning)
        elif owner_count == 1:
            alerts.append(Alert(
                alert_type='permissions',
                severity=Alert.SEVERITY_WARNING,
                title='Single Workspace Owner',
                message='Only one workspace owner - consider adding backup owners',
                details={'owner_count': 1}
            ))

        # If we have previous data, check for changes
        if previous_users:
            prev_users_dict = {u['id']: u for u in previous_users}
            current_users_dict = {u['id']: u for u in users}

            admin_changes = []

            for user_id in set(list(prev_users_dict.keys()) + list(current_users_dict.keys())):
                prev_user = prev_users_dict.get(user_id, {})
                curr_user = current_users_dict.get(user_id, {})

                # Check for admin status change
                if prev_user.get('is_admin') != curr_user.get('is_admin'):
                    admin_changes.append({
                        'user_id': user_id,
                        'name': curr_user.get('name', prev_user.get('name')),
                        'change': 'granted' if curr_user.get('is_admin') else 'revoked',
                        'role': 'admin'
                    })

                # Check for owner status change
                if prev_user.get('is_owner') != curr_user.get('is_owner'):
                    admin_changes.append({
                        'user_id': user_id,
                        'name': curr_user.get('name', prev_user.get('name')),
                        'change': 'granted' if curr_user.get('is_owner') else 'revoked',
                        'role': 'owner'
                    })

            if len(admin_changes) >= self.thresholds['admin_change_spike']:
                alerts.append(Alert(
                    alert_type='permissions',
                    severity=Alert.SEVERITY_WARNING,
                    title='Multiple Permission Changes',
                    message=f'{len(admin_changes)} admin/owner permission changes detected',
                    details={
                        'change_count': len(admin_changes),
                        'changes': admin_changes
                    }
                ))

        return alerts

    def check_storage(self, files: List[Dict]) -> List[Alert]:
        """
        Check workspace storage usage

        Args:
            files: List of file metadata dicts

        Returns:
            List of alerts
        """
        alerts = []

        # Calculate total storage
        total_bytes = sum(f.get('size', 0) for f in files)
        total_gb = total_bytes / (1024 ** 3)

        warning_threshold = self.thresholds['storage_warning_gb']
        critical_threshold = self.thresholds['storage_critical_gb']

        if total_gb >= critical_threshold:
            alerts.append(Alert(
                alert_type='storage',
                severity=Alert.SEVERITY_CRITICAL,
                title='Critical Storage Usage',
                message=f'Workspace storage at {total_gb:.2f} GB (critical threshold: {critical_threshold} GB)',
                details={
                    'total_gb': round(total_gb, 2),
                    'threshold': critical_threshold,
                    'file_count': len(files)
                }
            ))
        elif total_gb >= warning_threshold:
            alerts.append(Alert(
                alert_type='storage',
                severity=Alert.SEVERITY_WARNING,
                title='High Storage Usage',
                message=f'Workspace storage at {total_gb:.2f} GB (warning threshold: {warning_threshold} GB)',
                details={
                    'total_gb': round(total_gb, 2),
                    'threshold': warning_threshold,
                    'file_count': len(files)
                }
            ))

        return alerts

    def check_guest_accounts(self, users: List[Dict]) -> List[Alert]:
        """
        Check for high percentage of guest accounts

        Args:
            users: List of user dicts

        Returns:
            List of alerts
        """
        alerts = []

        active_users = [u for u in users if not u.get('deleted') and not u.get('is_bot')]
        guest_users = [u for u in active_users if u.get('is_restricted') or u.get('is_ultra_restricted')]

        if active_users:
            guest_percentage = (len(guest_users) / len(active_users) * 100)

            if guest_percentage > self.thresholds['guest_account_percentage']:
                alerts.append(Alert(
                    alert_type='security',
                    severity=Alert.SEVERITY_WARNING,
                    title='High Guest Account Percentage',
                    message=f'{len(guest_users)} guest accounts ({guest_percentage:.1f}% of workspace)',
                    details={
                        'guest_count': len(guest_users),
                        'total_users': len(active_users),
                        'percentage': round(guest_percentage, 2),
                        'threshold': self.thresholds['guest_account_percentage']
                    }
                ))

        return alerts

    def check_archived_channels(self, channels: List[Dict], previous_channels: List[Dict] = None, days: int = 7) -> List[Alert]:
        """
        Check for unusual spike in archived channels

        Args:
            channels: Current channel list
            previous_channels: Previous channel list for comparison
            days: Number of days to check

        Returns:
            List of alerts
        """
        alerts = []

        if previous_channels:
            prev_archived = {c['id']: c for c in previous_channels if c.get('is_archived')}
            curr_archived = {c['id']: c for c in channels if c.get('is_archived')}

            newly_archived = set(curr_archived.keys()) - set(prev_archived.keys())

            if len(newly_archived) >= self.thresholds['channel_archive_spike']:
                channels_list = [curr_archived[cid] for cid in newly_archived]
                alerts.append(Alert(
                    alert_type='channel_management',
                    severity=Alert.SEVERITY_WARNING,
                    title='Channel Archival Spike',
                    message=f'{len(newly_archived)} channels archived recently',
                    details={
                        'archived_count': len(newly_archived),
                        'channels': [{'id': c['id'], 'name': c.get('name')} for c in channels_list[:20]]
                    }
                ))

        return alerts

    def check_external_sharing(self, channels: List[Dict]) -> List[Alert]:
        """
        Check for channels with external sharing enabled

        Args:
            channels: List of channel dicts

        Returns:
            List of alerts
        """
        alerts = []

        # Check for external workspaces (is_ext_shared)
        external_channels = [c for c in channels if c.get('is_ext_shared') and not c.get('is_archived')]

        if len(external_channels) > self.thresholds['external_sharing_count']:
            alerts.append(Alert(
                alert_type='security',
                severity=Alert.SEVERITY_INFO,
                title='Multiple External Shared Channels',
                message=f'{len(external_channels)} channels are shared with external workspaces',
                details={
                    'external_count': len(external_channels),
                    'threshold': self.thresholds['external_sharing_count'],
                    'channels': [{'id': c['id'], 'name': c.get('name')} for c in external_channels[:20]]
                }
            ))

        return alerts

    def run_all_checks(self, workspace_data: Dict, previous_data: Dict = None) -> List[Alert]:
        """
        Run all checks and return all alerts

        Args:
            workspace_data: Current workspace data dict with users, channels, files
            previous_data: Previous workspace data for comparison

        Returns:
            List of all alerts
        """
        all_alerts = []

        users = workspace_data.get('users', [])
        channels = workspace_data.get('channels', [])
        files = workspace_data.get('files', [])

        previous_users = previous_data.get('users', []) if previous_data else None
        previous_channels = previous_data.get('channels', []) if previous_data else None

        # Run all checks
        all_alerts.extend(self.check_inactive_users(users))
        all_alerts.extend(self.check_recent_deactivations(users))
        all_alerts.extend(self.check_admin_changes(users, previous_users))
        all_alerts.extend(self.check_storage(files))
        all_alerts.extend(self.check_guest_accounts(users))
        all_alerts.extend(self.check_archived_channels(channels, previous_channels))
        all_alerts.extend(self.check_external_sharing(channels))

        return all_alerts


class AlertManager:
    """Manage and store alerts"""

    def __init__(self, alert_file: str = 'alerts.json'):
        """
        Initialize alert manager

        Args:
            alert_file: Path to JSON file for storing alerts
        """
        self.alert_file = Path(alert_file)
        self.alerts = []

    def add_alert(self, alert: Alert):
        """Add alert to manager"""
        self.alerts.append(alert)

    def add_alerts(self, alerts: List[Alert]):
        """Add multiple alerts"""
        self.alerts.extend(alerts)

    def get_alerts(self, severity: str = None, alert_type: str = None) -> List[Alert]:
        """
        Get filtered alerts

        Args:
            severity: Filter by severity
            alert_type: Filter by alert type

        Returns:
            Filtered list of alerts
        """
        filtered = self.alerts

        if severity:
            filtered = [a for a in filtered if a.severity == severity]

        if alert_type:
            filtered = [a for a in filtered if a.alert_type == alert_type]

        return filtered

    def get_summary(self) -> Dict:
        """Get alert summary statistics"""
        return {
            'total': len(self.alerts),
            'critical': len(self.get_alerts(severity=Alert.SEVERITY_CRITICAL)),
            'warning': len(self.get_alerts(severity=Alert.SEVERITY_WARNING)),
            'info': len(self.get_alerts(severity=Alert.SEVERITY_INFO)),
            'by_type': self._count_by_type()
        }

    def _count_by_type(self) -> Dict:
        """Count alerts by type"""
        counts = defaultdict(int)
        for alert in self.alerts:
            counts[alert.alert_type] += 1
        return dict(counts)

    def save(self):
        """Save alerts to file"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_summary(),
            'alerts': [a.to_dict() for a in self.alerts]
        }

        self.alert_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.alert_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load(self):
        """Load alerts from file"""
        if not self.alert_file.exists():
            return

        with open(self.alert_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Reconstruct alerts
        self.alerts = []
        for alert_data in data.get('alerts', []):
            alert = Alert(
                alert_type=alert_data['alert_type'],
                severity=alert_data['severity'],
                title=alert_data['title'],
                message=alert_data['message'],
                details=alert_data.get('details', {})
            )
            alert.timestamp = datetime.fromisoformat(alert_data['timestamp'])
            self.alerts.append(alert)

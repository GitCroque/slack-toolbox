"""
Integration tests for end-to-end workflows
"""

import pytest
from pathlib import Path


class TestWorkflows:
    """Test complete workflows"""

    def test_user_export_workflow(self, mock_slack_client, tmp_path):
        """Test complete user export workflow"""
        from lib.slack_client import SlackManager
        from lib.utils import save_to_csv

        # Initialize client
        slack = SlackManager()

        # Get users
        users = slack.list_users()
        assert len(users) > 0

        # Prepare export data
        export_data = []
        for user in users:
            export_data.append({
                'id': user['id'],
                'name': user['name'],
                'email': user.get('profile', {}).get('email', '')
            })

        # Export to CSV
        output_file = tmp_path / "users_export.csv"
        save_to_csv(export_data, str(output_file))

        # Verify export
        assert output_file.exists()
        content = output_file.read_text()
        assert 'testuser' in content

    def test_channel_listing_workflow(self, mock_slack_client):
        """Test channel listing workflow"""
        from lib.slack_client import SlackManager

        slack = SlackManager()
        channels = slack.list_channels()

        assert len(channels) > 0
        assert channels[0]['name'] == 'general'

    def test_stats_generation_workflow(self, mock_slack_client):
        """Test statistics generation workflow"""
        from lib.slack_client import SlackManager

        slack = SlackManager()
        stats = slack.get_user_stats()

        # Verify all required stats are present
        required_keys = ['total', 'active', 'deleted', 'bots', 'admins', 'owners', 'guests']
        for key in required_keys:
            assert key in stats
            assert isinstance(stats[key], int)

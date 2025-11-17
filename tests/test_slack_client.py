"""
Tests for Slack client functionality
"""

import pytest
from lib.slack_client import SlackManager


class TestSlackManager:
    """Test SlackManager class"""

    def test_initialization(self, mock_slack_client, temp_config_file):
        """Test client initialization"""
        slack = SlackManager(temp_config_file)
        assert slack.token is not None
        assert slack.max_retries == 3

    def test_list_users(self, mock_slack_client):
        """Test listing users"""
        slack = SlackManager()
        users = slack.list_users()

        assert isinstance(users, list)
        assert len(users) > 0
        assert 'id' in users[0]
        assert 'name' in users[0]

    def test_list_channels(self, mock_slack_client):
        """Test listing channels"""
        slack = SlackManager()
        channels = slack.list_channels()

        assert isinstance(channels, list)
        assert len(channels) > 0
        assert 'id' in channels[0]
        assert 'name' in channels[0]

    def test_get_user_stats(self, mock_slack_client):
        """Test getting user statistics"""
        slack = SlackManager()
        stats = slack.get_user_stats()

        assert 'total' in stats
        assert 'active' in stats
        assert 'admins' in stats
        assert stats['total'] >= 0


class TestErrorHandling:
    """Test error handling in Slack client"""

    def test_invalid_config_path(self):
        """Test handling of invalid config path"""
        with pytest.raises(FileNotFoundError):
            SlackManager('/nonexistent/config.json')

    def test_connection_test(self, mock_slack_client):
        """Test connection testing"""
        slack = SlackManager()
        result = slack.test_connection()
        assert result == True

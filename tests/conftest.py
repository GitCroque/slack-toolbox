"""
Test configuration and fixtures for pytest
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_slack_client(monkeypatch):
    """Mock Slack client for testing"""
    class MockSlackClient:
        def __init__(self, token):
            self.token = token

        def users_list(self, **kwargs):
            return {
                'ok': True,
                'members': [
                    {
                        'id': 'U123',
                        'name': 'testuser',
                        'deleted': False,
                        'is_bot': False,
                        'is_admin': False,
                        'profile': {
                            'email': 'test@example.com',
                            'real_name': 'Test User'
                        }
                    }
                ],
                'response_metadata': {'next_cursor': ''}
            }

        def conversations_list(self, **kwargs):
            return {
                'ok': True,
                'channels': [
                    {
                        'id': 'C123',
                        'name': 'general',
                        'is_private': False,
                        'is_archived': False,
                        'num_members': 10
                    }
                ],
                'response_metadata': {'next_cursor': ''}
            }

        def auth_test(self):
            return {
                'ok': True,
                'user': 'testbot',
                'team': 'Test Team',
                'team_id': 'T123'
            }

    from lib import slack_client
    original_webclient = slack_client.WebClient

    def mock_init(self, config_path=None):
        self.config = {
            'slack_token': 'xoxb-test-token',
            'max_retries': 3,
            'rate_limit_delay': 1
        }
        self.token = self.config['slack_token']
        self.client = MockSlackClient(self.token)
        self.max_retries = 3
        self.rate_limit_delay = 1

    monkeypatch.setattr(slack_client.SlackManager, '__init__', mock_init)

    return MockSlackClient


@pytest.fixture
def sample_users():
    """Sample user data for testing"""
    return [
        {
            'id': 'U001',
            'name': 'john',
            'deleted': False,
            'is_bot': False,
            'is_admin': True,
            'profile': {
                'email': 'john@example.com',
                'real_name': 'John Doe',
                'display_name': 'johnd'
            }
        },
        {
            'id': 'U002',
            'name': 'jane',
            'deleted': False,
            'is_bot': False,
            'is_admin': False,
            'profile': {
                'email': 'jane@example.com',
                'real_name': 'Jane Smith',
                'display_name': 'janes'
            }
        }
    ]


@pytest.fixture
def sample_channels():
    """Sample channel data for testing"""
    return [
        {
            'id': 'C001',
            'name': 'general',
            'is_private': False,
            'is_archived': False,
            'num_members': 50,
            'topic': {'value': 'General discussion'},
            'purpose': {'value': 'Company-wide announcements'}
        },
        {
            'id': 'C002',
            'name': 'engineering',
            'is_private': False,
            'is_archived': False,
            'num_members': 25,
            'topic': {'value': 'Engineering discussions'},
            'purpose': {'value': 'Tech team channel'}
        }
    ]


@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary config file for testing"""
    config_file = tmp_path / "config.json"
    config_file.write_text('''{
        "slack_token": "xoxb-test-token",
        "workspace_name": "TestWorkspace",
        "default_export_format": "csv",
        "timezone": "UTC"
    }''')
    return str(config_file)


@pytest.fixture
def temp_csv_file(tmp_path):
    """Create temporary CSV file for testing"""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text('''email,first_name,last_name,channels
test1@example.com,Test,One,"general,random"
test2@example.com,Test,Two,general
''')
    return str(csv_file)

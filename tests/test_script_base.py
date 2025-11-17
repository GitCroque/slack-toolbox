"""
Tests for SlackScript base class
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.script_base import SlackScript


class DummyScript(SlackScript):
    """Test script for testing base class"""

    def __init__(self, *args, execute_called=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.execute_called = execute_called
        self.setup_called = False
        self.cleanup_called = False

    def setup_arguments(self, parser):
        """Add test arguments"""
        parser.add_argument('--test-arg', default='test', help='Test argument')

    def validate_arguments(self):
        """Validate test arguments"""
        if hasattr(self.args, 'invalid') and self.args.invalid:
            raise ValueError("Invalid argument")

    def setup(self):
        """Setup hook"""
        self.setup_called = True

    def execute(self):
        """Execute main logic"""
        self.execute_called = True
        self.logger.info("Script executed")

    def cleanup(self):
        """Cleanup hook"""
        self.cleanup_called = True


class FailingScript(SlackScript):
    """Script that fails during execution"""

    def execute(self):
        raise RuntimeError("Execution failed")


class TestSlackScriptInitialization:
    """Test script initialization"""

    def test_init_with_defaults(self):
        """Test initialization with default parameters"""
        script = DummyScript('test_script', 'Test Description')
        assert script.name == 'test_script'
        assert script.description == 'Test Description'
        assert script.require_slack is True

    def test_init_without_slack(self):
        """Test initialization without Slack requirement"""
        script = DummyScript('test_script', 'Test Description', require_slack=False)
        assert script.require_slack is False


class TestArgumentParsing:
    """Test argument parsing"""

    def test_parser_creation(self):
        """Test parser creation with common arguments"""
        script = DummyScript('test_script', 'Test Description')
        parser = script.create_parser()

        assert parser is not None
        # Check common arguments are present
        args = parser.parse_args(['--dry-run', '--log-level', 'DEBUG'])
        assert args.dry_run is True
        assert args.log_level == 'DEBUG'

    def test_custom_arguments(self):
        """Test custom arguments from subclass"""
        script = DummyScript('test_script', 'Test Description')
        parser = script.create_parser()
        script.setup_arguments(parser)

        args = parser.parse_args(['--test-arg', 'custom'])
        assert args.test_arg == 'custom'


class TestScriptLifecycle:
    """Test script lifecycle management"""

    @patch('lib.script_base.setup_logger')
    @patch('lib.script_base.load_config')
    @patch('lib.script_base.SlackManager')
    def test_successful_run(self, mock_slack, mock_load_config, mock_logger):
        """Test successful script run"""
        # Setup mocks
        mock_logger.return_value = Mock()
        mock_load_config.return_value = {'slack_token': 'xoxb-test'}
        mock_slack.return_value = Mock()

        # Run script
        script = DummyScript('test_script', 'Test Description')

        with patch.object(sys, 'argv', ['script.py', '--config', 'config.json']):
            exit_code = script.run()

        # Verify lifecycle
        assert exit_code == 0
        assert script.setup_called is True
        assert script.execute_called is True
        assert script.cleanup_called is True

    @patch('lib.script_base.setup_logger')
    @patch('lib.script_base.load_config')
    def test_run_without_slack(self, mock_load_config, mock_logger):
        """Test run without Slack initialization"""
        mock_logger.return_value = Mock()
        mock_load_config.return_value = {}

        script = DummyScript('test_script', 'Test Description', require_slack=False)

        with patch.object(sys, 'argv', ['script.py']):
            exit_code = script.run()

        assert exit_code == 0
        assert script.slack is None

    @patch('lib.script_base.setup_logger')
    @patch('lib.script_base.load_config')
    @patch('lib.script_base.SlackManager')
    def test_cleanup_runs_on_failure(self, mock_slack, mock_load_config, mock_logger):
        """Test cleanup runs even when execute fails"""
        mock_logger.return_value = Mock()
        mock_load_config.return_value = {'slack_token': 'xoxb-test'}
        mock_slack.return_value = Mock()

        script = FailingScript('test_script', 'Test Description')
        script.cleanup_called = False

        def cleanup():
            script.cleanup_called = True

        script.cleanup = cleanup

        with patch.object(sys, 'argv', ['script.py']):
            exit_code = script.run()

        assert exit_code == 1
        assert script.cleanup_called is True


class TestErrorHandling:
    """Test error handling"""

    @patch('lib.script_base.setup_logger')
    @patch('lib.script_base.load_config')
    def test_missing_config_file(self, mock_load_config, mock_logger):
        """Test handling of missing config file"""
        mock_logger.return_value = Mock()
        mock_load_config.side_effect = FileNotFoundError("Config not found")

        script = DummyScript('test_script', 'Test Description')

        with patch.object(sys, 'argv', ['script.py']):
            exit_code = script.run()

        assert exit_code == 1

    @patch('lib.script_base.setup_logger')
    @patch('lib.script_base.load_config')
    @patch('lib.script_base.SlackManager')
    def test_slack_initialization_failure(self, mock_slack, mock_load_config, mock_logger):
        """Test handling of Slack initialization failure"""
        mock_logger.return_value = Mock()
        mock_load_config.return_value = {'slack_token': 'invalid'}
        mock_slack.side_effect = ValueError("Invalid token")

        script = DummyScript('test_script', 'Test Description')

        with patch.object(sys, 'argv', ['script.py']):
            exit_code = script.run()

        assert exit_code == 1

    @patch('lib.script_base.setup_logger')
    @patch('lib.script_base.load_config')
    @patch('lib.script_base.SlackManager')
    def test_execution_failure(self, mock_slack, mock_load_config, mock_logger):
        """Test handling of execution failure"""
        mock_logger.return_value = Mock()
        mock_load_config.return_value = {'slack_token': 'xoxb-test'}
        mock_slack.return_value = Mock()

        script = FailingScript('test_script', 'Test Description')

        with patch.object(sys, 'argv', ['script.py']):
            exit_code = script.run()

        assert exit_code == 1

    @patch('lib.script_base.setup_logger')
    @patch('lib.script_base.load_config')
    @patch('lib.script_base.SlackManager')
    def test_keyboard_interrupt(self, mock_slack, mock_load_config, mock_logger):
        """Test handling of keyboard interrupt"""
        mock_logger.return_value = Mock()
        mock_load_config.return_value = {'slack_token': 'xoxb-test'}
        mock_slack.return_value = Mock()

        script = DummyScript('test_script', 'Test Description')

        def raise_interrupt():
            raise KeyboardInterrupt()

        script.execute = raise_interrupt

        with patch.object(sys, 'argv', ['script.py']):
            exit_code = script.run()

        assert exit_code == 130


class TestDryRunMode:
    """Test dry-run mode"""

    @patch('lib.script_base.setup_logger')
    @patch('lib.script_base.load_config')
    @patch('lib.script_base.SlackManager')
    def test_dry_run_flag(self, mock_slack, mock_load_config, mock_logger):
        """Test dry-run flag is set correctly"""
        mock_logger.return_value = Mock()
        mock_load_config.return_value = {'slack_token': 'xoxb-test'}
        mock_slack.return_value = Mock()

        script = DummyScript('test_script', 'Test Description')

        with patch.object(sys, 'argv', ['script.py', '--dry-run']):
            script.run()

        assert script.args.dry_run is True

    def test_dry_run_check_true(self):
        """Test dry_run_check when in dry-run mode"""
        script = DummyScript('test_script', 'Test Description')
        script.args = Mock(dry_run=True)
        script.logger = Mock()

        result = script.dry_run_check("Test operation")

        assert result is True
        script.logger.info.assert_called_once()

    def test_dry_run_check_false(self):
        """Test dry_run_check when not in dry-run mode"""
        script = DummyScript('test_script', 'Test Description')
        script.args = Mock(dry_run=False)
        script.logger = Mock()

        result = script.dry_run_check("Test operation")

        assert result is False


class TestValidation:
    """Test argument validation"""

    @patch('lib.script_base.setup_logger')
    @patch('lib.script_base.load_config')
    @patch('lib.script_base.SlackManager')
    def test_validation_failure(self, mock_slack, mock_load_config, mock_logger):
        """Test validation failure"""
        mock_logger.return_value = Mock()
        mock_load_config.return_value = {'slack_token': 'xoxb-test'}
        mock_slack.return_value = Mock()

        script = DummyScript('test_script', 'Test Description')

        # Mock invalid arguments
        with patch.object(sys, 'argv', ['script.py']):
            script.args = Mock(invalid=True, dry_run=False, config='config.json', log_level='INFO')
            script.parser = script.create_parser()
            script.logger = mock_logger.return_value
            script.config = mock_load_config.return_value

            # Manually call validation which should fail
            try:
                script.validate_arguments()
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "Invalid argument" in str(e)


class TestSetupAndCleanupHooks:
    """Test setup and cleanup hooks"""

    @patch('lib.script_base.setup_logger')
    @patch('lib.script_base.load_config')
    @patch('lib.script_base.SlackManager')
    def test_setup_called(self, mock_slack, mock_load_config, mock_logger):
        """Test that setup hook is called"""
        mock_logger.return_value = Mock()
        mock_load_config.return_value = {'slack_token': 'xoxb-test'}
        mock_slack.return_value = Mock()

        script = DummyScript('test_script', 'Test Description')

        with patch.object(sys, 'argv', ['script.py']):
            script.run()

        assert script.setup_called is True

    @patch('lib.script_base.setup_logger')
    @patch('lib.script_base.load_config')
    @patch('lib.script_base.SlackManager')
    def test_cleanup_called(self, mock_slack, mock_load_config, mock_logger):
        """Test that cleanup hook is called"""
        mock_logger.return_value = Mock()
        mock_load_config.return_value = {'slack_token': 'xoxb-test'}
        mock_slack.return_value = Mock()

        script = DummyScript('test_script', 'Test Description')

        with patch.object(sys, 'argv', ['script.py']):
            script.run()

        assert script.cleanup_called is True

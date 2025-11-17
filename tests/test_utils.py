"""
Tests for utility functions
"""

import pytest
import json
from pathlib import Path
from lib.utils import (
    validate_email,
    sanitize_channel_name,
    format_bytes,
    similar,
    save_to_csv,
    load_csv,
    save_to_json,
    load_json,
    load_config,
    format_timestamp,
    parse_timestamp,
    days_ago,
    confirm_action,
    get_user_display_name,
    create_backup_filename,
    ensure_directory,
    batch_process,
)
from datetime import datetime


class TestEmailValidation:
    """Test email validation"""

    def test_valid_emails(self):
        assert validate_email('test@example.com') == True
        assert validate_email('user.name@company.co.uk') == True
        assert validate_email('admin+tag@domain.org') == True

    def test_invalid_emails(self):
        assert validate_email('invalid') == False
        assert validate_email('@example.com') == False
        assert validate_email('test@') == False
        assert validate_email('') == False


class TestChannelNameSanitization:
    """Test channel name sanitization"""

    def test_lowercase_conversion(self):
        assert sanitize_channel_name('UPPERCASE') == 'uppercase'

    def test_space_to_hyphen(self):
        assert sanitize_channel_name('my channel') == 'my-channel'

    def test_special_characters_removed(self):
        assert sanitize_channel_name('channel@#$%name') == 'channelname'

    def test_length_limit(self):
        long_name = 'a' * 100
        result = sanitize_channel_name(long_name)
        assert len(result) <= 80

    def test_leading_trailing_hyphens(self):
        assert sanitize_channel_name('-channel-') == 'channel'


class TestFormatBytes:
    """Test byte formatting"""

    def test_bytes(self):
        assert format_bytes(100) == '100.0 B'

    def test_kilobytes(self):
        assert format_bytes(1024) == '1.0 KB'

    def test_megabytes(self):
        assert format_bytes(1024 * 1024) == '1.0 MB'

    def test_gigabytes(self):
        assert format_bytes(1024 * 1024 * 1024) == '1.0 GB'


class TestCSVOperations:
    """Test CSV save/load operations"""

    def test_save_and_load_csv(self, tmp_path):
        # Test data
        data = [
            {'name': 'John', 'email': 'john@example.com'},
            {'name': 'Jane', 'email': 'jane@example.com'}
        ]

        # Save
        csv_file = tmp_path / "test.csv"
        save_to_csv(data, str(csv_file))

        # Verify file exists
        assert csv_file.exists()

        # Load and verify
        loaded_data = load_csv(str(csv_file))
        assert len(loaded_data) == 2
        assert loaded_data[0]['name'] == 'John'
        assert loaded_data[1]['email'] == 'jane@example.com'


class TestSimilarity:
    """Test string similarity function"""

    def test_identical_strings(self):
        """Test similarity of identical strings"""
        assert similar('test', 'test') == 1.0

    def test_different_strings(self):
        """Test similarity of different strings"""
        ratio = similar('abc', 'xyz')
        assert ratio < 0.5

    def test_similar_strings(self):
        """Test similarity of similar strings"""
        ratio = similar('John Doe', 'John Do')
        assert ratio > 0.8


class TestJSONOperations:
    """Test JSON save/load operations"""

    def test_save_and_load_json(self, tmp_path):
        """Test JSON save and load"""
        data = {'name': 'John', 'age': 30, 'city': 'Paris'}

        # Save
        json_file = tmp_path / "test.json"
        save_to_json(data, str(json_file))

        # Verify file exists
        assert json_file.exists()

        # Load and verify
        loaded_data = load_json(str(json_file))
        assert loaded_data == data

    def test_save_json_pretty_print(self, tmp_path):
        """Test JSON pretty printing"""
        data = {'a': 1, 'b': 2}
        json_file = tmp_path / "pretty.json"

        save_to_json(data, str(json_file), pretty=True)

        # Check that file is formatted
        content = json_file.read_text()
        assert '\n' in content


class TestTimestampFunctions:
    """Test timestamp formatting functions"""

    def test_format_timestamp(self):
        """Test timestamp formatting"""
        ts = 1609459200.0  # 2021-01-01 00:00:00 UTC
        result = format_timestamp(ts)
        assert '2021' in result

    def test_parse_timestamp_with_time(self):
        """Test parsing date with time"""
        date_str = '2021-01-01 12:00:00'
        ts = parse_timestamp(date_str)
        assert ts > 0

    def test_parse_timestamp_date_only(self):
        """Test parsing date only"""
        date_str = '2021-01-01'
        ts = parse_timestamp(date_str)
        assert ts > 0

    def test_days_ago(self):
        """Test days_ago function"""
        ts = days_ago(7)
        now = datetime.now().timestamp()
        # Should be approximately 7 days ago (within 1 day tolerance)
        assert abs((now - ts) - (7 * 24 * 3600)) < 24 * 3600


class TestUserDisplayName:
    """Test user display name extraction"""

    def test_display_name_from_profile(self):
        """Test getting display name from profile"""
        user = {
            'id': 'U123',
            'name': 'john',
            'profile': {'display_name': 'John D.'}
        }
        assert get_user_display_name(user) == 'John D.'

    def test_real_name_fallback(self):
        """Test fallback to real_name"""
        user = {
            'id': 'U123',
            'name': 'john',
            'profile': {'real_name': 'John Doe'}
        }
        assert get_user_display_name(user) == 'John Doe'

    def test_username_fallback(self):
        """Test fallback to username"""
        user = {
            'id': 'U123',
            'name': 'john',
            'profile': {}
        }
        assert get_user_display_name(user) == 'john'


class TestBackupFilename:
    """Test backup filename generation"""

    def test_create_backup_filename(self):
        """Test backup filename generation"""
        filename = create_backup_filename('users', 'csv')
        assert filename.startswith('users_')
        assert filename.endswith('.csv')
        assert len(filename) > len('users_.csv')


class TestEnsureDirectory:
    """Test directory creation"""

    def test_ensure_directory_creates(self, tmp_path):
        """Test that directory is created"""
        new_dir = tmp_path / "test_dir"
        ensure_directory(str(new_dir))
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_directory_nested(self, tmp_path):
        """Test nested directory creation"""
        nested = tmp_path / "a" / "b" / "c"
        ensure_directory(str(nested))
        assert nested.exists()

    def test_ensure_directory_already_exists(self, tmp_path):
        """Test that existing directory is OK"""
        existing = tmp_path / "existing"
        existing.mkdir()
        ensure_directory(str(existing))  # Should not raise
        assert existing.exists()


class TestBatchProcess:
    """Test batch processing generator"""

    def test_batch_process_basic(self):
        """Test basic batch processing"""
        items = list(range(100))
        batches = list(batch_process(items, batch_size=10, delay=0))

        assert len(batches) == 10
        assert len(batches[0]) == 10
        assert batches[0] == list(range(10))

    def test_batch_process_uneven(self):
        """Test batch processing with uneven division"""
        items = list(range(25))
        batches = list(batch_process(items, batch_size=10, delay=0))

        assert len(batches) == 3
        assert len(batches[-1]) == 5  # Last batch has 5 items

    def test_batch_process_single_batch(self):
        """Test batch processing with single batch"""
        items = list(range(5))
        batches = list(batch_process(items, batch_size=10, delay=0))

        assert len(batches) == 1
        assert batches[0] == items


class TestLoadConfig:
    """Test configuration loading"""

    def test_load_config_with_path(self, tmp_path):
        """Test loading config from specific path"""
        config_file = tmp_path / "config.json"
        config_data = {'slack_token': 'xoxb-test', 'max_retries': 3}
        config_file.write_text(json.dumps(config_data))

        config = load_config(str(config_file))
        assert config == config_data

    def test_load_config_nonexistent_raises_error(self, tmp_path):
        """Test that nonexistent config raises error"""
        with pytest.raises(FileNotFoundError):
            load_config(str(tmp_path / "nonexistent.json"))

    def test_load_config_invalid_json_raises_error(self, tmp_path):
        """Test that invalid JSON raises error"""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("not valid json {")

        with pytest.raises(json.JSONDecodeError):
            load_config(str(config_file))

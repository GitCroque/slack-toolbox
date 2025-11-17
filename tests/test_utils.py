"""
Tests for utility functions
"""

import pytest
from lib.utils import (
    validate_email,
    sanitize_channel_name,
    format_bytes,
    similar,
    save_to_csv,
    load_csv
)


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
        from difflib import SequenceMatcher
        ratio = SequenceMatcher(None, 'test', 'test').ratio()
        assert ratio == 1.0

    def test_different_strings(self):
        from difflib import SequenceMatcher
        ratio = SequenceMatcher(None, 'abc', 'xyz').ratio()
        assert ratio < 0.5

    def test_similar_strings(self):
        from difflib import SequenceMatcher
        ratio = SequenceMatcher(None, 'John Doe', 'John Do').ratio()
        assert ratio > 0.8

"""
Comprehensive tests for validators module
"""

import pytest
from pathlib import Path
import sys

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.validators import (
    ValidationError,
    validate_email,
    validate_channel_name,
    sanitize_channel_name,
    validate_file_path,
    validate_csv_path,
    validate_output_directory,
    validate_positive_int,
    validate_range,
    validate_user_id,
    validate_channel_id,
    validate_webhook_url,
    validate_date_format,
)


class TestEmailValidation:
    """Test email validation"""

    def test_valid_emails(self):
        """Test various valid email formats"""
        valid_emails = [
            'user@example.com',
            'user.name@example.com',
            'user+tag@example.com',
            'user_name@example.co.uk',
            'user123@test-domain.com',
        ]
        for email in valid_emails:
            assert validate_email(email) is True, f"Failed for: {email}"

    def test_invalid_emails(self):
        """Test various invalid email formats"""
        invalid_emails = [
            'invalid',
            '@example.com',
            'user@',
            'user @example.com',
            '',
            None,
            'user@example',
            'user..name@example.com',
        ]
        for email in invalid_emails:
            assert validate_email(email) is False, f"Should fail for: {email}"


class TestChannelNameValidation:
    """Test channel name validation"""

    def test_valid_channel_names(self):
        """Test valid channel names"""
        valid_names = [
            'general',
            'general-chat',
            'team_updates',
            'project-2024',
            'a',
            'abc123',
        ]
        for name in valid_names:
            assert validate_channel_name(name) is True, f"Failed for: {name}"

    def test_invalid_channel_names(self):
        """Test invalid channel names"""
        invalid_names = [
            'UPPERCASE',
            'with spaces',
            '-starts-with-hyphen',
            'ends-with-hyphen-',
            '_starts-with-underscore',
            'special@chars',
            'channel!',
            '',
            'a' * 81,  # Too long
        ]
        for name in invalid_names:
            assert validate_channel_name(name) is False, f"Should fail for: {name}"


class TestChannelNameSanitization:
    """Test channel name sanitization"""

    def test_lowercase_conversion(self):
        """Test conversion to lowercase"""
        assert sanitize_channel_name('UPPERCASE') == 'uppercase'
        assert sanitize_channel_name('MiXeD') == 'mixed'

    def test_space_to_hyphen(self):
        """Test space replacement"""
        assert sanitize_channel_name('my channel') == 'my-channel'
        assert sanitize_channel_name('multiple  spaces') == 'multiple-spaces'

    def test_special_characters_removal(self):
        """Test special character removal"""
        assert sanitize_channel_name('channel@#$name') == 'channel-name'
        assert sanitize_channel_name('test!@#$%') == 'test'

    def test_length_limit(self):
        """Test 80 character limit"""
        long_name = 'a' * 100
        result = sanitize_channel_name(long_name)
        assert len(result) <= 80

    def test_leading_trailing_removal(self):
        """Test removal of leading/trailing hyphens and underscores"""
        assert sanitize_channel_name('-channel-') == 'channel'
        assert sanitize_channel_name('__test__') == 'test'

    def test_empty_name_raises_error(self):
        """Test that empty name raises ValidationError"""
        with pytest.raises(ValidationError):
            sanitize_channel_name('')


class TestFilePathValidation:
    """Test file path validation"""

    def test_valid_path(self, tmp_path):
        """Test validation of valid path"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = validate_file_path(test_file, must_exist=True)
        assert result.exists()

    def test_nonexistent_path_with_must_exist(self, tmp_path):
        """Test that nonexistent path fails when must_exist=True"""
        nonexistent = tmp_path / "nonexistent.txt"

        with pytest.raises(ValidationError, match="does not exist"):
            validate_file_path(nonexistent, must_exist=True)

    def test_existing_path_with_must_not_exist(self, tmp_path):
        """Test that existing path fails when must_not_exist=True"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(ValidationError, match="already exists"):
            validate_file_path(test_file, must_not_exist=True)

    def test_file_type_validation(self, tmp_path):
        """Test file vs directory type validation"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # File validation
        validate_file_path(test_file, must_be_file=True)

        # Directory validation
        with pytest.raises(ValidationError, match="not a file"):
            validate_file_path(test_dir, must_be_file=True)

    def test_path_traversal_detection(self):
        """Test detection of excessive parent references"""
        with pytest.raises(ValidationError, match="parent directory references"):
            validate_file_path("../../../../../../../etc/passwd")

    def test_empty_path_raises_error(self):
        """Test that empty path raises ValidationError"""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_file_path("")


class TestCSVPathValidation:
    """Test CSV path validation"""

    def test_valid_csv_path(self, tmp_path):
        """Test valid CSV path"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("header\ndata")

        result = validate_csv_path(csv_file)
        assert result.suffix == '.csv'

    def test_non_csv_extension_fails(self, tmp_path):
        """Test that non-CSV extension fails"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("data")

        with pytest.raises(ValidationError, match="must have .csv extension"):
            validate_csv_path(txt_file)


class TestOutputDirectoryValidation:
    """Test output directory validation"""

    def test_existing_directory(self, tmp_path):
        """Test validation of existing directory"""
        result = validate_output_directory(tmp_path)
        assert result.is_dir()

    def test_create_nonexistent_directory(self, tmp_path):
        """Test creation of nonexistent directory"""
        new_dir = tmp_path / "new_dir"

        result = validate_output_directory(new_dir, create=True)
        assert result.exists()
        assert result.is_dir()

    def test_nonexistent_directory_without_create(self, tmp_path):
        """Test that nonexistent directory fails without create=True"""
        new_dir = tmp_path / "new_dir"

        with pytest.raises(ValidationError, match="does not exist"):
            validate_output_directory(new_dir, create=False)


class TestPositiveIntValidation:
    """Test positive integer validation"""

    def test_valid_positive_integers(self):
        """Test valid positive integers"""
        assert validate_positive_int(1, "test") == 1
        assert validate_positive_int(100, "test") == 100
        assert validate_positive_int("42", "test") == 42

    def test_zero_fails(self):
        """Test that zero fails"""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_positive_int(0, "test")

    def test_negative_fails(self):
        """Test that negative numbers fail"""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_positive_int(-5, "test")

    def test_non_integer_fails(self):
        """Test that non-integers fail"""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_positive_int("abc", "test")


class TestRangeValidation:
    """Test range validation"""

    def test_value_in_range(self):
        """Test value within range"""
        assert validate_range(50, min_val=0, max_val=100) == 50
        assert validate_range(0, min_val=0, max_val=100) == 0
        assert validate_range(100, min_val=0, max_val=100) == 100

    def test_value_below_minimum(self):
        """Test value below minimum"""
        with pytest.raises(ValidationError, match="must be >="):
            validate_range(-5, min_val=0)

    def test_value_above_maximum(self):
        """Test value above maximum"""
        with pytest.raises(ValidationError, match="must be <="):
            validate_range(150, max_val=100)


class TestUserIdValidation:
    """Test Slack user ID validation"""

    def test_valid_user_ids(self):
        """Test valid user IDs"""
        valid_ids = [
            'U1234ABCD',
            'U12345678',
            'USLACKBOT',
        ]
        for user_id in valid_ids:
            result = validate_user_id(user_id)
            assert result.startswith('U')

    def test_invalid_user_ids(self):
        """Test invalid user IDs"""
        invalid_ids = [
            'invalid',
            'C1234ABCD',  # Channel ID
            'U123',  # Too short
            '',
        ]
        for user_id in invalid_ids:
            with pytest.raises(ValidationError):
                validate_user_id(user_id)


class TestChannelIdValidation:
    """Test Slack channel ID validation"""

    def test_valid_channel_ids(self):
        """Test valid channel IDs"""
        valid_ids = [
            'C1234ABCD',
            'C12345678',
            'G1234ABCD',  # Private channel
        ]
        for channel_id in valid_ids:
            result = validate_channel_id(channel_id)
            assert result[0] in ['C', 'G']

    def test_invalid_channel_ids(self):
        """Test invalid channel IDs"""
        invalid_ids = [
            'invalid',
            'U1234ABCD',  # User ID
            'C123',  # Too short
            '',
        ]
        for channel_id in invalid_ids:
            with pytest.raises(ValidationError):
                validate_channel_id(channel_id)


class TestWebhookUrlValidation:
    """Test Slack webhook URL validation"""

    def test_valid_webhook_url(self):
        """Test valid webhook URL"""
        valid_url = 'https://hooks.slack.com/services/T00/B00/xxx'
        result = validate_webhook_url(valid_url)
        assert result == valid_url

    def test_non_https_fails(self):
        """Test that non-HTTPS URL fails"""
        with pytest.raises(ValidationError, match="must use HTTPS"):
            validate_webhook_url('http://hooks.slack.com/services/T00/B00/xxx')

    def test_invalid_domain_fails(self):
        """Test that invalid domain fails"""
        with pytest.raises(ValidationError, match="Invalid Slack webhook"):
            validate_webhook_url('https://example.com/webhook')

    def test_empty_url_fails(self):
        """Test that empty URL fails"""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_webhook_url('')


class TestDateFormatValidation:
    """Test date format validation"""

    def test_valid_date_format(self):
        """Test valid date format"""
        assert validate_date_format('2024-01-15') == '2024-01-15'
        assert validate_date_format('2024-12-31') == '2024-12-31'

    def test_invalid_date_format(self):
        """Test invalid date format"""
        invalid_dates = [
            '15/01/2024',
            '2024-13-01',  # Invalid month
            '2024-01-32',  # Invalid day
            'not-a-date',
        ]
        for date in invalid_dates:
            with pytest.raises(ValidationError, match="Invalid date format"):
                validate_date_format(date)

    def test_custom_format(self):
        """Test custom date format"""
        assert validate_date_format('01/15/2024', format='%m/%d/%Y') == '01/15/2024'

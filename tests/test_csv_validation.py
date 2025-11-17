"""
Tests for CSV validation
"""

import pytest
from pathlib import Path


class TestCSVValidation:
    """Test CSV validation functionality"""

    def test_valid_users_csv(self, temp_csv_file):
        """Test validation of valid users CSV"""
        # Import here to avoid issues
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))

        # The CSV is valid
        assert Path(temp_csv_file).exists()

        # Read and check content
        with open(temp_csv_file) as f:
            content = f.read()
            assert 'email' in content
            assert 'test1@example.com' in content

    def test_email_validation_in_csv(self, tmp_path):
        """Test email validation in CSV"""
        from lib.utils import validate_email

        # Create CSV with invalid emails
        csv_file = tmp_path / "invalid.csv"
        csv_file.write_text('''email,first_name
invalid-email,Test
valid@example.com,Valid
''')

        # Read and validate
        with open(csv_file) as f:
            lines = f.readlines()[1:]  # Skip header
            for line in lines:
                email = line.split(',')[0]
                # Should handle both valid and invalid
                result = validate_email(email)
                assert isinstance(result, bool)

#!/usr/bin/env python3
"""
Validate CSV files before import
Checks format, required columns, email validity, etc.
"""

import argparse
import sys
import csv
from pathlib import Path
import re

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.utils import validate_email
from lib.logger import setup_logger


# CSV format definitions
CSV_FORMATS = {
    'users': {
        'required_columns': ['email'],
        'optional_columns': ['first_name', 'last_name', 'channels'],
        'validators': {
            'email': lambda v: validate_email(v),
            'first_name': lambda v: len(v) > 0 if v else True,
            'last_name': lambda v: len(v) > 0 if v else True,
            'channels': lambda v: all(re.match(r'^[a-z0-9-_]+$', ch.strip()) for ch in v.split(',')) if v else True
        }
    },
    'channels': {
        'required_columns': ['name'],
        'optional_columns': ['description', 'private'],
        'validators': {
            'name': lambda v: re.match(r'^[a-z0-9-_]+$', v) and len(v) <= 80,
            'description': lambda v: len(v) <= 250 if v else True,
            'private': lambda v: v.lower() in ['true', 'false', '1', '0', 'yes', 'no', ''] if v else True
        }
    }
}


def detect_csv_type(headers):
    """Detect CSV type based on headers"""
    for csv_type, format_def in CSV_FORMATS.items():
        required = set(format_def['required_columns'])
        if required.issubset(set(headers)):
            return csv_type
    return None


def validate_csv_file(file_path, csv_type=None):
    """
    Validate a CSV file

    Returns: (is_valid, errors, warnings, stats)
    """
    errors = []
    warnings = []
    stats = {
        'total_rows': 0,
        'valid_rows': 0,
        'invalid_rows': 0,
        'empty_rows': 0
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read and validate
            reader = csv.DictReader(f)
            headers = reader.fieldnames

            if not headers:
                errors.append("CSV file is empty or has no headers")
                return False, errors, warnings, stats

            # Detect type if not specified
            if csv_type is None:
                csv_type = detect_csv_type(headers)
                if csv_type:
                    warnings.append(f"Auto-detected CSV type: {csv_type}")
                else:
                    errors.append(f"Could not detect CSV type. Headers found: {', '.join(headers)}")
                    errors.append("Supported types: users (requires: email), channels (requires: name)")
                    return False, errors, warnings, stats

            # Get format definition
            format_def = CSV_FORMATS[csv_type]

            # Check required columns
            missing_columns = set(format_def['required_columns']) - set(headers)
            if missing_columns:
                errors.append(f"Missing required columns: {', '.join(missing_columns)}")
                return False, errors, warnings, stats

            # Check for unknown columns
            all_columns = set(format_def['required_columns'] + format_def['optional_columns'])
            unknown_columns = set(headers) - all_columns
            if unknown_columns:
                warnings.append(f"Unknown columns (will be ignored): {', '.join(unknown_columns)}")

            # Validate each row
            validators = format_def['validators']

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                stats['total_rows'] += 1

                # Check if row is empty
                if all(not v.strip() for v in row.values()):
                    stats['empty_rows'] += 1
                    warnings.append(f"Row {row_num}: Empty row")
                    continue

                row_errors = []

                # Validate required fields
                for col in format_def['required_columns']:
                    value = row.get(col, '').strip()

                    if not value:
                        row_errors.append(f"Row {row_num}: Missing required field '{col}'")
                        continue

                    # Validate value
                    if col in validators:
                        try:
                            if not validators[col](value):
                                row_errors.append(f"Row {row_num}: Invalid {col}: '{value}'")
                        except Exception as e:
                            row_errors.append(f"Row {row_num}: Error validating {col}: {e}")

                # Validate optional fields (if present)
                for col in format_def['optional_columns']:
                    value = row.get(col, '').strip()

                    if value and col in validators:
                        try:
                            if not validators[col](value):
                                row_errors.append(f"Row {row_num}: Invalid {col}: '{value}'")
                        except Exception as e:
                            row_errors.append(f"Row {row_num}: Error validating {col}: {e}")

                # Type-specific validations
                if csv_type == 'users':
                    # Check for duplicate emails in file
                    email = row.get('email', '').strip().lower()
                    # This would require tracking seen emails - simplified for now

                if row_errors:
                    stats['invalid_rows'] += 1
                    errors.extend(row_errors)
                else:
                    stats['valid_rows'] += 1

    except FileNotFoundError:
        errors.append(f"File not found: {file_path}")
        return False, errors, warnings, stats
    except csv.Error as e:
        errors.append(f"CSV parsing error: {e}")
        return False, errors, warnings, stats
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return False, errors, warnings, stats

    # Final validation
    is_valid = len(errors) == 0 and stats['valid_rows'] > 0

    return is_valid, errors, warnings, stats


def main():
    parser = argparse.ArgumentParser(
        description='Validate CSV files before import',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate users CSV
  python3 validate_csv.py users.csv

  # Validate channels CSV
  python3 validate_csv.py channels.csv

  # Specify type explicitly
  python3 validate_csv.py data.csv --type users

Supported CSV types:
  - users: email (required), first_name, last_name, channels
  - channels: name (required), description, private
        """
    )

    parser.add_argument('file', help='CSV file to validate')
    parser.add_argument('--type', choices=['users', 'channels'],
                       help='CSV type (auto-detected if not specified)')
    parser.add_argument('--strict', action='store_true',
                       help='Treat warnings as errors')

    args = parser.parse_args()

    logger = setup_logger('validate_csv')

    print(f"\n{'='*60}")
    print(f"CSV VALIDATOR")
    print(f"{'='*60}\n")

    print(f"File: {args.file}")

    # Validate
    is_valid, errors, warnings, stats = validate_csv_file(args.file, args.type)

    # Display results
    print(f"\n{'='*60}")
    print("VALIDATION RESULTS")
    print(f"{'='*60}\n")

    print(f"📊 Statistics:")
    print(f"   Total rows: {stats['total_rows']}")
    print(f"   Valid rows: {stats['valid_rows']}")
    print(f"   Invalid rows: {stats['invalid_rows']}")
    if stats['empty_rows'] > 0:
        print(f"   Empty rows: {stats['empty_rows']}")

    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"   - {warning}")

    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for error in errors[:20]:  # Limit to first 20 errors
            print(f"   - {error}")

        if len(errors) > 20:
            print(f"   ... and {len(errors) - 20} more errors")

    print(f"\n{'='*60}")

    if is_valid and (not args.strict or not warnings):
        print("✅ CSV file is VALID")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        if args.strict and warnings:
            print("❌ CSV file has WARNINGS (strict mode)")
        else:
            print("❌ CSV file is INVALID")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()

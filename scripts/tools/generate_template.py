#!/usr/bin/env python3
"""
Generate CSV templates for bulk operations
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.utils import save_to_csv
from lib.logger import setup_logger


TEMPLATES = {
    'users': {
        'headers': ['email', 'first_name', 'last_name', 'channels'],
        'examples': [
            {
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'channels': 'general,random'
            },
            {
                'email': 'jane.smith@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'channels': 'general,engineering'
            },
        ],
        'description': 'Template for inviting users in bulk'
    },
    'channels': {
        'headers': ['name', 'description', 'private'],
        'examples': [
            {
                'name': 'project-alpha',
                'description': 'Discussion for Project Alpha',
                'private': 'false'
            },
            {
                'name': 'team-leads',
                'description': 'Leadership team discussions',
                'private': 'true'
            },
        ],
        'description': 'Template for creating channels in bulk'
    },
}


def generate_template(template_type, output_file=None, with_examples=True):
    """Generate a CSV template"""

    if template_type not in TEMPLATES:
        raise ValueError(f"Unknown template type: {template_type}")

    template = TEMPLATES[template_type]

    # Prepare data
    if with_examples:
        data = template['examples']
    else:
        # Just headers
        data = [{h: '' for h in template['headers']}]

    # Generate filename if not specified
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"{template_type}_template_{timestamp}.csv"

    # Save
    save_to_csv(data, output_file, fieldnames=template['headers'])

    return output_file, template['description']


def main():
    parser = argparse.ArgumentParser(
        description='Generate CSV templates for bulk operations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate users template with examples
  python3 generate_template.py --type users

  # Generate empty channels template
  python3 generate_template.py --type channels --no-examples

  # Specify output file
  python3 generate_template.py --type users --output my_users.csv

Available templates:
  - users: For bulk user invitations
  - channels: For bulk channel creation
        """
    )

    parser.add_argument('--type', '-t', required=True,
                       choices=list(TEMPLATES.keys()),
                       help='Template type')
    parser.add_argument('--output', '-o',
                       help='Output filename (auto-generated if not specified)')
    parser.add_argument('--no-examples', action='store_true',
                       help='Generate template without example rows')

    args = parser.parse_args()

    logger = setup_logger('generate_template')

    try:
        output_file, description = generate_template(
            args.type,
            args.output,
            with_examples=not args.no_examples
        )

        print(f"\n✅ Template generated: {output_file}")
        print(f"   {description}")

        if not args.no_examples:
            print(f"\n💡 Edit this file and add your data, then run:")
            if args.type == 'users':
                print(f"   python3 scripts/users/invite_users.py --file {output_file}")
            elif args.type == 'channels':
                print(f"   python3 scripts/channels/create_channels.py --file {output_file}")

            print(f"\n💡 Or use make command:")
            if args.type == 'users':
                print(f"   make invite-users FILE={output_file}")
            elif args.type == 'channels':
                print(f"   make create-channels FILE={output_file}")

        print()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

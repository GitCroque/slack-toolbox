#!/usr/bin/env python3
"""
Test Slack API connection and verify configuration
"""

import sys
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.slack_client import SlackManager
from lib.logger import setup_logger


def main():
    logger = setup_logger('test_connection')

    try:
        print("\n" + "="*50)
        print("TESTING SLACK API CONNECTION")
        print("="*50 + "\n")

        # Initialize Slack client
        slack = SlackManager()

        # Test connection
        if slack.test_connection():
            print("\n✅ Configuration is correct!")
            print("   You can now use the Slack management scripts.")
        else:
            print("\n❌ Connection test failed")
            print("   Please check your configuration in config/config.json")
            sys.exit(1)

        print("="*50 + "\n")

    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        print("\nQuick setup:")
        print("1. Copy config/config.example.json to config/config.json")
        print("2. Get your Slack token from https://api.slack.com/apps")
        print("3. Update the slack_token in config/config.json\n")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ {e}\n")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

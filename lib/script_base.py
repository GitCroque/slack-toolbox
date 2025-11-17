"""
Base class for Slack management scripts to reduce boilerplate code.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .logger import setup_logger
from .slack_client import SlackManager
from .utils import load_config


class SlackScript:
    """
    Base class for Slack management scripts.

    Handles common functionality:
    - Argument parsing
    - Logger setup
    - Slack client initialization
    - Error handling
    - Configuration loading

    Usage:
        class MyScript(SlackScript):
            def setup_arguments(self, parser):
                parser.add_argument('--my-arg', help='My argument')

            def execute(self):
                # Your script logic here
                self.logger.info("Running script")
                users = self.slack.list_users()
                # ...

        if __name__ == '__main__':
            MyScript('my_script', 'Description of my script').run()
    """

    def __init__(
        self,
        name: str,
        description: str,
        config_path: str = "config/config.json",
        require_slack: bool = True,
    ):
        """
        Initialize the script.

        Args:
            name: Script name (used for logging)
            description: Script description (shown in help)
            config_path: Path to configuration file
            require_slack: Whether to initialize Slack client (default: True)
        """
        self.name = name
        self.description = description
        self.config_path = config_path
        self.require_slack = require_slack

        self.parser: Optional[argparse.ArgumentParser] = None
        self.args: Optional[argparse.Namespace] = None
        self.logger = None
        self.slack: Optional[SlackManager] = None
        self.config: Optional[dict] = None

    def create_parser(self) -> argparse.ArgumentParser:
        """
        Create argument parser with common arguments.

        Returns:
            ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description=self.description, formatter_class=argparse.RawDescriptionHelpFormatter
        )

        # Common arguments
        parser.add_argument("--config", default=self.config_path, help="Path to config file")

        parser.add_argument(
            "--log-level",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            help="Logging level",
        )

        parser.add_argument("--dry-run", action="store_true", help="Dry run mode (don't make changes)")

        return parser

    def setup_arguments(self, parser: argparse.ArgumentParser):
        """
        Add script-specific arguments to parser.

        Override this method in subclasses to add custom arguments.

        Args:
            parser: ArgumentParser instance

        Example:
            def setup_arguments(self, parser):
                parser.add_argument('--user', required=True, help='User ID')
                parser.add_argument('--role', choices=['admin', 'user'], help='User role')
        """
        pass

    def validate_arguments(self):
        """
        Validate parsed arguments.

        Override this method in subclasses to add custom validation.

        Raises:
            ValueError: If arguments are invalid

        Example:
            def validate_arguments(self):
                if self.args.days < 1:
                    raise ValueError("Days must be positive")
        """
        pass

    def setup(self):
        """
        Setup hook called before execute().

        Override this method to perform setup operations like
        loading additional configuration, validating files, etc.

        Example:
            def setup(self):
                if not os.path.exists(self.args.file):
                    raise FileNotFoundError(f"File not found: {self.args.file}")
        """
        pass

    def execute(self):
        """
        Main script logic.

        Override this method with your script's logic.

        Raises:
            NotImplementedError: If not implemented by subclass

        Example:
            def execute(self):
                self.logger.info("Fetching users...")
                users = self.slack.list_users()
                self.logger.info(f"Found {len(users)} users")
                for user in users:
                    print(f"- {user['name']}")
        """
        raise NotImplementedError("Subclass must implement execute() method")

    def cleanup(self):
        """
        Cleanup hook called after execute() (even if it fails).

        Override this method to perform cleanup operations like
        closing files, releasing resources, etc.

        Example:
            def cleanup(self):
                if hasattr(self, 'output_file'):
                    self.output_file.close()
        """
        pass

    def run(self):
        """
        Run the script with full lifecycle management.

        This method:
        1. Creates argument parser
        2. Parses arguments
        3. Sets up logger
        4. Loads configuration
        5. Initializes Slack client (if required)
        6. Validates arguments
        7. Runs setup hook
        8. Executes main logic
        9. Runs cleanup hook
        10. Handles errors gracefully

        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            # Parse arguments
            self.parser = self.create_parser()
            self.setup_arguments(self.parser)
            self.args = self.parser.parse_args()

            # Setup logger
            self.logger = setup_logger(self.name, level=self.args.log_level)

            # Load configuration
            try:
                self.config = load_config(self.args.config)
            except FileNotFoundError:
                self.logger.error(f"Configuration file not found: {self.args.config}")
                self.logger.error("Run setup wizard: python3 setup_wizard.py")
                return 1
            except Exception as e:
                self.logger.error(f"Failed to load configuration: {e}")
                return 1

            # Dry run notification
            if self.args.dry_run:
                self.logger.warning("🔍 DRY RUN MODE - No changes will be made")

            # Initialize Slack client
            if self.require_slack:
                try:
                    self.slack = SlackManager(config_path=self.args.config)
                    self.logger.debug("Slack client initialized")
                except Exception as e:
                    self.logger.error(f"Failed to initialize Slack client: {e}")
                    return 1

            # Validate arguments
            try:
                self.validate_arguments()
            except ValueError as e:
                self.logger.error(f"Invalid arguments: {e}")
                return 1

            # Run setup hook
            try:
                self.setup()
            except Exception as e:
                self.logger.error(f"Setup failed: {e}")
                return 1

            # Execute main logic
            self.logger.debug(f"Starting {self.name}...")
            self.execute()
            self.logger.info("✅ Script completed successfully")

            return 0

        except KeyboardInterrupt:
            self.logger.warning("\n⚠️  Interrupted by user")
            return 130

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Script failed: {e}")
                self.logger.debug("Exception details:", exc_info=True)
            else:
                print(f"❌ Error: {e}", file=sys.stderr)
            return 1

        finally:
            # Always run cleanup
            try:
                self.cleanup()
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Cleanup failed: {e}")

    def dry_run_check(self, operation: str) -> bool:
        """
        Check if we're in dry-run mode and log the operation.

        Args:
            operation: Description of the operation that would be performed

        Returns:
            True if this is a dry run (operation should be skipped), False otherwise

        Example:
            if self.dry_run_check(f"Would create channel: {channel_name}"):
                return
            # Proceed with actual creation
        """
        if self.args.dry_run:
            self.logger.info(f"[DRY RUN] {operation}")
            return True
        return False

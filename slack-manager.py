#!/usr/bin/env python3
"""
Interactive CLI for Slack Management Platform
User-friendly menu interface for common operations
"""

import sys
from pathlib import Path
import subprocess

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.slack_client import SlackManager
from lib.logger import setup_logger


class SlackManagerCLI:
    """Interactive CLI for Slack management"""

    def __init__(self):
        self.logger = setup_logger('slack-manager-cli')
        self.slack = None

    def clear_screen(self):
        """Clear the terminal screen"""
        subprocess.run(['clear'], check=False)

    def print_header(self):
        """Print application header"""
        print("\n" + "="*60)
        print("  SLACK MANAGEMENT PLATFORM - Interactive CLI")
        print("="*60 + "\n")

    def print_menu(self, title, options):
        """Print a menu"""
        print(f"\n{title}")
        print("-" * len(title))

        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        print(f"{len(options) + 1}. Back/Exit")
        print()

    def get_choice(self, max_choice):
        """Get user choice"""
        while True:
            try:
                choice = input("Enter your choice: ").strip()
                choice_num = int(choice)

                if 1 <= choice_num <= max_choice + 1:
                    return choice_num
                else:
                    print(f"❌ Please enter a number between 1 and {max_choice + 1}")
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                sys.exit(0)

    def run_script(self, script_path, *args):
        """Run a Python script"""
        try:
            cmd = [sys.executable, script_path] + list(args)
            subprocess.run(cmd, check=True)
            input("\n\nPress Enter to continue...")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error running script: {e}")
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled")
            input("\nPress Enter to continue...")

    def user_management_menu(self):
        """User management submenu"""
        while True:
            self.clear_screen()
            self.print_header()

            options = [
                "List all users",
                "List administrators",
                "List guest users",
                "Export users to CSV",
                "User statistics",
                "Search users",
                "Invite users from CSV",
            ]

            self.print_menu("USER MANAGEMENT", options)
            choice = self.get_choice(len(options))

            if choice == 1:
                self.run_script("scripts/users/list_users.py")
            elif choice == 2:
                self.run_script("scripts/users/list_users.py", "--role", "admin")
            elif choice == 3:
                self.run_script("scripts/users/list_users.py", "--role", "guest")
            elif choice == 4:
                self.run_script("scripts/users/export_users.py", "--format", "csv")
            elif choice == 5:
                self.run_script("scripts/users/user_stats.py")
            elif choice == 6:
                query = input("\nEnter search query: ")
                self.run_script("scripts/utils/search.py", "--query", query, "--type", "user")
            elif choice == 7:
                csv_file = input("\nEnter CSV file path: ")
                self.run_script("scripts/users/invite_users.py", "--file", csv_file)
            else:
                break

    def channel_management_menu(self):
        """Channel management submenu"""
        while True:
            self.clear_screen()
            self.print_header()

            options = [
                "List all channels",
                "List channels (including private & archived)",
                "Find inactive channels",
                "Search channels",
                "Create channels from CSV",
            ]

            self.print_menu("CHANNEL MANAGEMENT", options)
            choice = self.get_choice(len(options))

            if choice == 1:
                self.run_script("scripts/channels/list_channels.py")
            elif choice == 2:
                self.run_script("scripts/channels/list_channels.py", "--include-private", "--include-archived")
            elif choice == 3:
                days = input("\nDays of inactivity (default: 90): ") or "90"
                self.run_script("scripts/channels/find_inactive.py", "--days", days)
            elif choice == 4:
                query = input("\nEnter search query: ")
                self.run_script("scripts/utils/search.py", "--query", query, "--type", "channel")
            elif choice == 5:
                csv_file = input("\nEnter CSV file path: ")
                self.run_script("scripts/channels/create_channels.py", "--file", csv_file)
            else:
                break

    def audit_menu(self):
        """Audit and reports submenu"""
        while True:
            self.clear_screen()
            self.print_header()

            options = [
                "Permissions audit",
                "Find inactive users",
                "Find duplicate users",
                "File report",
                "Activity report",
                "Export channel history",
            ]

            self.print_menu("AUDIT & REPORTS", options)
            choice = self.get_choice(len(options))

            if choice == 1:
                self.run_script("scripts/audit/permissions_audit.py")
            elif choice == 2:
                days = input("\nDays of inactivity (default: 60): ") or "60"
                self.run_script("scripts/audit/inactive_users.py", "--days", days)
            elif choice == 3:
                self.run_script("scripts/audit/find_duplicates.py")
            elif choice == 4:
                self.run_script("scripts/audit/file_report.py")
            elif choice == 5:
                days = input("\nPeriod in days (default: 30): ") or "30"
                self.run_script("scripts/audit/activity_report.py", "--days", days)
            elif choice == 6:
                channel = input("\nEnter channel name: ")
                self.run_script("scripts/audit/export_channel_history.py", "--channel", channel)
            else:
                break

    def utilities_menu(self):
        """Utilities submenu"""
        while True:
            self.clear_screen()
            self.print_header()

            options = [
                "Workspace statistics",
                "Full backup",
                "Universal search",
                "Validate CSV file",
                "Generate CSV template",
                "Test connection",
            ]

            self.print_menu("UTILITIES", options)
            choice = self.get_choice(len(options))

            if choice == 1:
                self.run_script("scripts/utils/workspace_stats.py")
            elif choice == 2:
                include_msgs = input("\nInclude message history? (y/N): ").lower() == 'y'
                if include_msgs:
                    self.run_script("scripts/utils/full_backup.py", "--include-messages", "--message-limit", "500")
                else:
                    self.run_script("scripts/utils/full_backup.py")
            elif choice == 3:
                query = input("\nEnter search query: ")
                self.run_script("scripts/utils/search.py", "--query", query)
            elif choice == 4:
                csv_file = input("\nEnter CSV file path: ")
                self.run_script("scripts/utils/validate_csv.py", csv_file)
            elif choice == 5:
                print("\nTemplate types: users, channels")
                template_type = input("Enter type: ")
                if template_type in ['users', 'channels']:
                    self.run_script("scripts/utils/generate_template.py", "--type", template_type)
                else:
                    print("Invalid type")
                    input("\nPress Enter to continue...")
            elif choice == 6:
                self.run_script("scripts/utils/test_connection.py")
            else:
                break

    def main_menu(self):
        """Main menu"""
        while True:
            self.clear_screen()
            self.print_header()

            # Test connection if not done
            if self.slack is None:
                try:
                    self.slack = SlackManager()
                    workspace_info = self.slack.get_workspace_info()
                    workspace_name = workspace_info.get('team', {}).get('name', 'Unknown')
                    print(f"✅ Connected to: {workspace_name}\n")
                except Exception as e:
                    print(f"⚠️  Not connected to Slack: {e}")
                    print("   Please configure your token in config/config.json\n")

            options = [
                "User Management",
                "Channel Management",
                "Audit & Reports",
                "Utilities",
            ]

            self.print_menu("MAIN MENU", options)
            choice = self.get_choice(len(options))

            if choice == 1:
                self.user_management_menu()
            elif choice == 2:
                self.channel_management_menu()
            elif choice == 3:
                self.audit_menu()
            elif choice == 4:
                self.utilities_menu()
            else:
                print("\n👋 Goodbye!")
                break

    def run(self):
        """Run the interactive CLI"""
        try:
            self.main_menu()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)


if __name__ == '__main__':
    cli = SlackManagerCLI()
    cli.run()

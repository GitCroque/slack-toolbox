#!/usr/bin/env python3
"""
Interactive configuration wizard for Slack Management Platform
Guides users through complete setup
"""

import sys
import json
import subprocess
from pathlib import Path


class Colors:
    """Terminal colors"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")


def prompt_input(question, default=None):
    """Prompt for user input"""
    if default:
        question += f" [{default}]"

    response = input(f"{Colors.CYAN}❓ {question}: {Colors.END}").strip()

    if not response and default:
        return default

    return response


def prompt_yes_no(question, default=True):
    """Prompt for yes/no question"""
    choices = " [Y/n]" if default else " [y/N]"
    response = input(f"{Colors.CYAN}❓ {question}{choices}: {Colors.END}").strip().lower()

    if not response:
        return default

    return response in ['y', 'yes', 'oui']


def check_python_version():
    """Check Python version"""
    print_info("Checking Python version...")

    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print_error(f"Python 3.8+ required. Found: {version.major}.{version.minor}")
        return False


def check_pip():
    """Check pip installation"""
    print_info("Checking pip...")

    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'],
                      check=True, capture_output=True)
        print_success("pip is installed")
        return True
    except:
        print_error("pip not found")
        return False


def install_dependencies():
    """Install Python dependencies"""
    if not prompt_yes_no("Install Python dependencies?", True):
        print_warning("Skipping dependencies installation")
        return True

    print_info("Installing dependencies...")

    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            check=True
        )
        print_success("Dependencies installed successfully")
        return True
    except Exception as e:
        print_error(f"Failed to install dependencies: {e}")
        return False


def setup_slack_token():
    """Guide user through Slack token setup"""
    print_header("SLACK API TOKEN SETUP")

    print("\n📚 How to get your Slack API token:\n")
    print("1. Go to https://api.slack.com/apps")
    print("2. Click 'Create New App' or select existing app")
    print("3. Go to 'OAuth & Permissions'")
    print("4. Add required Bot Token Scopes (see README.md)")
    print("5. Install app to your workspace")
    print("6. Copy the 'Bot User OAuth Token' (starts with xoxb-)")

    print()

    if prompt_yes_no("Open Slack API website in browser?", False):
        import webbrowser
        webbrowser.open("https://api.slack.com/apps")
        print_info("Opened https://api.slack.com/apps in your browser")

    print()

    token = prompt_input("Enter your Slack Bot Token (xoxb-...)")

    while not token or not token.startswith('xoxb-'):
        print_error("Invalid token. Must start with 'xoxb-'")
        token = prompt_input("Enter your Slack Bot Token (xoxb-...)")

    return token


def setup_config():
    """Setup configuration file"""
    print_header("CONFIGURATION SETUP")

    config_path = Path("config/config.json")

    if config_path.exists():
        if not prompt_yes_no("Config file exists. Overwrite?", False):
            print_warning("Keeping existing configuration")
            return True

    # Get Slack token
    token = setup_slack_token()

    # Get workspace name
    print()
    workspace_name = prompt_input("Enter workspace name (for display)", "MyWorkspace")

    # Get timezone
    print()
    timezone = prompt_input("Enter timezone", "Europe/Paris")

    # Export format
    print()
    print("Default export format:")
    print("  1. CSV")
    print("  2. JSON")
    export_choice = prompt_input("Choose [1-2]", "1")
    export_format = "csv" if export_choice == "1" else "json"

    # Webhook (optional)
    print()
    webhook_url = ""
    if prompt_yes_no("Configure Slack webhook for notifications?", False):
        webhook_url = prompt_input("Enter webhook URL")

    # Create config
    config = {
        "slack_token": token,
        "workspace_name": workspace_name,
        "default_export_format": export_format,
        "timezone": timezone,
        "log_level": "INFO",
        "max_retries": 3,
        "rate_limit_delay": 1,
        "backup_directory": "backups",
        "export_directory": "exports"
    }

    if webhook_url:
        config["webhook_url"] = webhook_url

    # Save config
    try:
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print_success(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        print_error(f"Failed to save config: {e}")
        return False


def test_connection():
    """Test Slack API connection"""
    print_header("CONNECTION TEST")

    if not prompt_yes_no("Test Slack API connection?", True):
        print_warning("Skipping connection test")
        return True

    print_info("Testing connection...")

    try:
        result = subprocess.run(
            [sys.executable, 'scripts/utils/test_connection.py'],
            check=True,
            capture_output=True,
            text=True
        )

        print(result.stdout)
        print_success("Connection test passed!")
        return True
    except subprocess.CalledProcessError as e:
        print_error("Connection test failed")
        print(e.stdout if e.stdout else e.stderr)
        return False


def setup_cron_jobs():
    """Guide user through cron setup"""
    print_header("AUTOMATION SETUP (Optional)")

    if not prompt_yes_no("Setup automated tasks (cron jobs)?", False):
        print_warning("Skipping automation setup")
        return True

    print()
    print("Available automation scripts:")
    print("  1. Daily backup (2:00 AM)")
    print("  2. Weekly inactive user report (Monday 9:00 AM)")
    print("  3. Monthly security audit (1st of month, 8:00 AM)")
    print()

    print_info("To setup cron jobs:")
    print("1. Edit crontab:")
    print(f"   {Colors.YELLOW}crontab -e{Colors.END}")
    print()
    print("2. Add these lines:")
    print(f"   {Colors.YELLOW}0 2 * * * {Path.cwd()}/cron/daily_backup.sh{Colors.END}")
    print(f"   {Colors.YELLOW}0 9 * * 1 {Path.cwd()}/cron/weekly_inactive_report.sh{Colors.END}")
    print(f"   {Colors.YELLOW}0 8 1 * * {Path.cwd()}/cron/monthly_audit.sh{Colors.END}")
    print()

    # Make cron scripts executable
    try:
        subprocess.run(['chmod', '+x', 'cron/daily_backup.sh'], check=True)
        subprocess.run(['chmod', '+x', 'cron/weekly_inactive_report.sh'], check=True)
        subprocess.run(['chmod', '+x', 'cron/monthly_audit.sh'], check=True)
        print_success("Cron scripts are now executable")
    except:
        print_warning("Could not make cron scripts executable")

    return True


def show_next_steps():
    """Show next steps to user"""
    print_header("SETUP COMPLETE!")

    print(f"\n{Colors.GREEN}✅ Your Slack Management Platform is ready!{Colors.END}\n")

    print("📚 Next steps:\n")
    print(f"1. View all available commands:")
    print(f"   {Colors.YELLOW}make help{Colors.END}\n")

    print(f"2. Get workspace statistics:")
    print(f"   {Colors.YELLOW}make stats{Colors.END}\n")

    print(f"3. Try the interactive CLI:")
    print(f"   {Colors.YELLOW}make interactive{Colors.END}\n")

    print(f"4. Create your first backup:")
    print(f"   {Colors.YELLOW}make backup{Colors.END}\n")

    print("📖 Documentation:")
    print("   - README.md - Complete guide")
    print("   - QUICKSTART.md - Quick start guide")
    print("   - FAQ.md - Troubleshooting")
    print("   - SLACK_API_GUIDE.md - API documentation")
    print()

    print(f"{Colors.BOLD}Happy Slack managing! 🚀{Colors.END}\n")


def main():
    """Main wizard flow"""
    print_header("SLACK MANAGEMENT PLATFORM SETUP WIZARD")

    print(f"\n{Colors.BOLD}Welcome!{Colors.END} This wizard will guide you through the setup process.\n")

    # Check prerequisites
    if not check_python_version():
        print_error("Please upgrade Python to 3.8 or higher")
        sys.exit(1)

    if not check_pip():
        print_error("Please install pip first")
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        if not prompt_yes_no("Continue without installing dependencies?", False):
            sys.exit(1)

    # Setup config
    if not setup_config():
        print_error("Configuration setup failed")
        sys.exit(1)

    # Test connection
    if not test_connection():
        print_warning("Connection test failed. Check your token and permissions.")

    # Setup automation
    setup_cron_jobs()

    # Show next steps
    show_next_steps()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)

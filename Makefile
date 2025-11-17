# Makefile for Slack Management Platform
# Simplifies common commands

.PHONY: help install test clean backup stats

# Python interpreter
PYTHON := python3

# Config file
CONFIG := config/config.json

# Default target
.DEFAULT_GOAL := help

##@ General

help: ## Display this help message
	@echo "Slack Management Platform - Available Commands"
	@echo "=============================================="
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

install: ## Install dependencies and setup configuration
	@echo "📦 Installing dependencies..."
	@$(PYTHON) -m pip install -r requirements.txt
	@if [ ! -f $(CONFIG) ]; then \
		echo "📝 Creating config file..."; \
		cp config/config.example.json $(CONFIG); \
		echo "⚠️  Please edit config/config.json with your Slack token"; \
	else \
		echo "✅ Config file already exists"; \
	fi
	@echo "✅ Installation complete!"

test: ## Test Slack API connection
	@echo "🧪 Testing Slack connection..."
	@$(PYTHON) scripts/tools/test_connection.py

clean: ## Clean generated files and caches
	@echo "🧹 Cleaning..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned!"

##@ User Management

list-users: ## List all users
	@$(PYTHON) scripts/users/list_users.py

list-admins: ## List all administrators
	@$(PYTHON) scripts/users/list_users.py --role admin

list-guests: ## List all guest users
	@$(PYTHON) scripts/users/list_users.py --role guest

export-users: ## Export users to CSV
	@$(PYTHON) scripts/users/export_users.py --format csv

export-users-json: ## Export users to JSON
	@$(PYTHON) scripts/users/export_users.py --format json

user-stats: ## Display user statistics
	@$(PYTHON) scripts/users/user_stats.py

invite-users: ## Invite users from CSV (usage: make invite-users FILE=users.csv)
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Error: FILE parameter required"; \
		echo "Usage: make invite-users FILE=users.csv"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/users/invite_users.py --file $(FILE)

deactivate-user: ## Deactivate a user (usage: make deactivate-user EMAIL=user@example.com)
	@if [ -z "$(EMAIL)" ]; then \
		echo "❌ Error: EMAIL parameter required"; \
		echo "Usage: make deactivate-user EMAIL=user@example.com"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/users/deactivate_user.py --email $(EMAIL)

##@ Channel Management

list-channels: ## List all channels
	@$(PYTHON) scripts/channels/list_channels.py

list-channels-all: ## List all channels including private and archived
	@$(PYTHON) scripts/channels/list_channels.py --include-private --include-archived

create-channels: ## Create channels from CSV (usage: make create-channels FILE=channels.csv)
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Error: FILE parameter required"; \
		echo "Usage: make create-channels FILE=channels.csv"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/channels/create_channels.py --file $(FILE)

archive-channel: ## Archive a channel (usage: make archive-channel NAME=old-project)
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Error: NAME parameter required"; \
		echo "Usage: make archive-channel NAME=channel-name"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/channels/archive_channel.py --name $(NAME)

find-inactive: ## Find inactive channels (default: 90 days)
	@$(PYTHON) scripts/channels/find_inactive.py --days $(or $(DAYS),90)

##@ Audit & Reports

audit-permissions: ## Run permissions audit
	@$(PYTHON) scripts/audit/permissions_audit.py

audit-permissions-csv: ## Export permissions audit to CSV
	@$(PYTHON) scripts/audit/permissions_audit.py --export permissions_audit.csv

inactive-users: ## Find inactive users (default: 60 days)
	@$(PYTHON) scripts/audit/inactive_users.py --days $(or $(DAYS),60)

file-report: ## Generate file report
	@$(PYTHON) scripts/audit/file_report.py --limit 100

export-channel: ## Export channel history (usage: make export-channel CHANNEL=general)
	@if [ -z "$(CHANNEL)" ]; then \
		echo "❌ Error: CHANNEL parameter required"; \
		echo "Usage: make export-channel CHANNEL=general"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/audit/export_channel_history.py --channel $(CHANNEL)

##@ Utilities

stats: ## Display workspace statistics
	@$(PYTHON) scripts/reports/workspace_stats.py

backup: ## Create full workspace backup
	@echo "💾 Creating backup..."
	@$(PYTHON) scripts/backup/create_backup.py --output-dir backups
	@echo "✅ Backup complete!"

backup-full: ## Create full backup including messages
	@echo "💾 Creating full backup with message history..."
	@$(PYTHON) scripts/backup/create_backup.py --output-dir backups --include-messages --message-limit 500
	@echo "✅ Full backup complete!"

search: ## Universal search (usage: make search QUERY=john)
	@if [ -z "$(QUERY)" ]; then \
		echo "❌ Error: QUERY parameter required"; \
		echo "Usage: make search QUERY=john"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/tools/search.py --query "$(QUERY)"

validate-csv: ## Validate CSV file (usage: make validate-csv FILE=users.csv)
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Error: FILE parameter required"; \
		echo "Usage: make validate-csv FILE=users.csv"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/tools/validate_csv.py $(FILE)

template: ## Generate CSV template (usage: make template TYPE=users)
	@if [ -z "$(TYPE)" ]; then \
		echo "❌ Error: TYPE parameter required"; \
		echo "Usage: make template TYPE=users (or channels)"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/tools/generate_template.py --type $(TYPE)

find-duplicates: ## Find duplicate users
	@$(PYTHON) scripts/audit/find_duplicates.py

activity-report: ## Generate activity report (usage: make activity-report DAYS=30)
	@$(PYTHON) scripts/audit/activity_report.py --days $(or $(DAYS),30)

dashboard: ## Generate HTML dashboard
	@$(PYTHON) scripts/reports/generate_dashboard.py
	@echo "✅ Dashboard generated: dashboard.html"

##@ Enterprise Features

setup-wizard: ## Run interactive configuration wizard
	@$(PYTHON) setup_wizard.py

export-pdf: ## Export users to PDF (usage: make export-pdf TYPE=users OUTPUT=report.pdf)
	@if [ -z "$(TYPE)" ]; then \
		echo "❌ Error: TYPE parameter required"; \
		echo "Usage: make export-pdf TYPE=users OUTPUT=report.pdf"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/reports/export_pdf.py --type $(TYPE) $(if $(OUTPUT),--output $(OUTPUT),)

notify: ## Send Slack notification (usage: make notify MSG="Backup complete")
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: MSG parameter required"; \
		echo "Usage: make notify MSG=\"Your message here\""; \
		exit 1; \
	fi
	@$(PYTHON) scripts/monitoring/send_notification.py --message "$(MSG)" $(if $(TYPE),--type $(TYPE),)

smart-alerts: ## Run intelligent alerting system
	@$(PYTHON) scripts/monitoring/smart_alerts.py

smart-alerts-notify: ## Run smart alerts with notifications
	@$(PYTHON) scripts/monitoring/smart_alerts.py --notify

smart-alerts-compare: ## Run smart alerts with comparison to previous snapshot
	@$(PYTHON) scripts/monitoring/smart_alerts.py --compare --notify

compare-backups: ## Compare two backups (usage: make compare-backups B1=backup1 B2=backup2)
	@if [ -z "$(B1)" ] || [ -z "$(B2)" ]; then \
		echo "❌ Error: B1 and B2 parameters required"; \
		echo "Usage: make compare-backups B1=backups/2024-01-01 B2=backups/2024-01-15"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/backup/compare_backups.py $(B1) $(B2) $(if $(FORMAT),--format $(FORMAT),)

##@ Interactive

interactive: ## Start interactive CLI
	@$(PYTHON) slack-manager.py

##@ Development

lint: ## Run linting (requires pylint)
	@echo "🔍 Running linting..."
	@$(PYTHON) -m pylint scripts/ lib/ || true

format: ## Format code (requires black)
	@echo "✨ Formatting code..."
	@$(PYTHON) -m black scripts/ lib/ || echo "Install black: pip install black"

check: ## Check code quality
	@echo "🔍 Checking code..."
	@$(PYTHON) -m pyflakes scripts/ lib/ || echo "Install pyflakes: pip install pyflakes"

run-tests: ## Run pytest test suite
	@echo "🧪 Running tests..."
	@pytest tests/ -v

test-coverage: ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	@pytest tests/ -v --cov=lib --cov=scripts --cov-report=html --cov-report=term
	@echo "📊 Coverage report: htmlcov/index.html"

pre-commit-install: ## Install pre-commit hooks
	@echo "🎣 Installing pre-commit hooks..."
	@pre-commit install
	@echo "✅ Pre-commit hooks installed!"

pre-commit-run: ## Run pre-commit on all files
	@echo "🎣 Running pre-commit checks..."
	@pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	@echo "🎣 Updating pre-commit hooks..."
	@pre-commit autoupdate

##@ Examples

example-onboard: ## Example: Onboard new users
	@echo "Example: Onboarding users from examples/users.csv"
	@$(PYTHON) scripts/users/invite_users.py --file examples/users.csv --dry-run

example-cleanup: ## Example: Find channels to cleanup
	@echo "Example: Finding inactive channels (90+ days)"
	@$(PYTHON) scripts/channels/find_inactive.py --days 90

example-audit: ## Example: Security audit
	@echo "Example: Running security audit"
	@$(PYTHON) scripts/audit/permissions_audit.py

##@ Quick Actions

quick-stats: stats ## Quick alias for stats

quick-backup: backup ## Quick alias for backup

quick-audit: audit-permissions ## Quick alias for audit

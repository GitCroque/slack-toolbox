#!/bin/bash
#
# Monthly Security Audit
# Comprehensive audit on the 1st of each month
#
# Add to crontab with: crontab -e
# 0 8 1 * * /path/to/slack-script/cron/monthly_audit.sh
#

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Create exports directory
mkdir -p "$SCRIPT_DIR/exports"

# Log file
LOG_FILE="$SCRIPT_DIR/logs/monthly_audit_$(date +%Y%m).log"
mkdir -p "$SCRIPT_DIR/logs"

# Date suffix for files
DATE_SUFFIX=$(date +%Y%m)

# Run comprehensive audit
{
    echo "=========================================="
    echo "Monthly Security Audit - $(date)"
    echo "=========================================="
    echo ""

    echo "1. Permissions Audit"
    python3 scripts/audit/permissions_audit.py --export "exports/permissions_audit_${DATE_SUFFIX}.csv"
    echo ""

    echo "2. Inactive Users (60+ days)"
    python3 scripts/audit/inactive_users.py --days 60 --export "exports/inactive_users_${DATE_SUFFIX}.csv"
    echo ""

    echo "3. Duplicate Detection"
    python3 scripts/audit/find_duplicates.py --export "exports/duplicates_${DATE_SUFFIX}.csv"
    echo ""

    echo "4. Activity Report"
    python3 scripts/audit/activity_report.py --days 30 --output "exports/activity_report_${DATE_SUFFIX}.json"
    echo ""

    echo "5. Workspace Statistics"
    python3 scripts/utils/workspace_stats.py
    echo ""

    echo "=========================================="
    echo "Monthly audit completed at $(date)"
    echo "=========================================="

} >> "$LOG_FILE" 2>&1

# Generate summary dashboard
python3 scripts/utils/generate_dashboard.py --output "exports/dashboard_${DATE_SUFFIX}.html" >> "$LOG_FILE" 2>&1

echo "Audit complete. Check $LOG_FILE for details"

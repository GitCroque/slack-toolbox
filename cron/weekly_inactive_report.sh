#!/bin/bash
#
# Weekly Inactive Users Report
# Generates report of inactive users every Monday
#
# Add to crontab with: crontab -e
# 0 9 * * 1 /path/to/slack-script/cron/weekly_inactive_report.sh
#

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Create exports directory
mkdir -p "$SCRIPT_DIR/exports"

# Log file
LOG_FILE="$SCRIPT_DIR/logs/weekly_inactive_$(date +%Y%m%d).log"
mkdir -p "$SCRIPT_DIR/logs"

# Output file
EXPORT_FILE="$SCRIPT_DIR/exports/inactive_users_$(date +%Y%m%d).csv"

# Run report
{
    echo "=========================================="
    echo "Weekly Inactive Report - $(date)"
    echo "=========================================="

    python3 scripts/audit/inactive_users.py --days 30 --export "$EXPORT_FILE"

    echo "Report generated at $(date)"
    echo "Output: $EXPORT_FILE"
    echo ""
} >> "$LOG_FILE" 2>&1

# Optional: Send email notification (requires mailx or mail command)
# if [ -f "$EXPORT_FILE" ]; then
#     mail -s "Weekly Inactive Users Report" admin@example.com < "$EXPORT_FILE"
# fi

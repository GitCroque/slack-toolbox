#!/bin/bash
#
# Daily Backup Script
# Backs up Slack workspace every day
#
# Add to crontab with: crontab -e
# 0 2 * * * /path/to/slack-script/cron/daily_backup.sh
#

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Log file
LOG_FILE="$SCRIPT_DIR/logs/daily_backup_$(date +%Y%m%d).log"
mkdir -p "$SCRIPT_DIR/logs"

# Run backup
{
    echo "=========================================="
    echo "Daily Backup - $(date)"
    echo "=========================================="

    python3 scripts/utils/full_backup.py --output-dir backups

    echo "Backup completed at $(date)"
    echo ""
} >> "$LOG_FILE" 2>&1

# Clean old backups (keep last 30 days)
find "$SCRIPT_DIR/backups" -type d -name "slack_backup_*" -mtime +30 -exec rm -rf {} + 2>/dev/null || true

# Clean old logs (keep last 90 days)
find "$SCRIPT_DIR/logs" -type f -name "*.log" -mtime +90 -delete 2>/dev/null || true

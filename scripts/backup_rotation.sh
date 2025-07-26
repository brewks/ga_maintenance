#!/bin/bash

# Default configuration
BACKUP_DIR="../database/backups"
LOG_FILE="../logs/rotation.log"
DAYS_TO_KEEP=7

# Create directories if they don't exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Verify there are backups to rotate
if [ -z "$(ls -A "$BACKUP_DIR"/*.db 2>/dev/null)" ]; then
    echo "$(date) - No backups found in $BACKUP_DIR" >> "$LOG_FILE"
    exit 0
fi

# Rotate backups
echo "=== Rotation started at $(date) ===" >> "$LOG_FILE"
find "$BACKUP_DIR" -name "*.db" -mtime +$DAYS_TO_KEEP -print -delete >> "$LOG_FILE" 2>&1
echo "=== Rotation completed ===" >> "$LOG_FILE"

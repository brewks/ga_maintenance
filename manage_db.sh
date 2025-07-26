#!/bin/bash
DB="database/ga_maintenance.db"
BACKUP_DIR="backups"
LOG="cron_backup.log"

echo "=== Backup started at $(date) ===" >> $LOG
mkdir -p "$BACKUP_DIR"
timestamp=$(date +%Y%m%d_%H%M%S)
cp "$DB" "$BACKUP_DIR/ga_maintenance_$timestamp.db" && \
echo "Success: Created $BACKUP_DIR/ga_maintenance_$timestamp.db" >> $LOG || \
echo "Error: Backup failed" >> $LOG

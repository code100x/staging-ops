#!/bin/bash

# Load environment variables from the .env file
export $(grep -v '^#' /path/to/.env | xargs)

# Backup filename with timestamp
TIMESTAMP=$(date +"%F")
BACKUP_FILE="$BACKUP_PATH/db_backup_$TIMESTAMP.sql"

# Dump the database
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > $BACKUP_FILE

# Upload the backup to Bunny Storage
curl -T $BACKUP_FILE -u $BUNNY_ACCESS_KEY: $BUNNY_STORAGE_URL$(basename $BACKUP_FILE)

# Remove local backup file after upload
rm $BACKUP_FILE


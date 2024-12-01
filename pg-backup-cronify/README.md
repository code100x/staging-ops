# Postgres Nightly Backup to Bunny CDN

This repo is having a setup to schedule backups of a Postgre DB, using Docker, `pg_dump`, and a Golang script to handle backup creation and upload to Bunny CDN. It would then exit out to minimize the system load.

## Overview

- **Database Backup**: Uses `pg_dump` to create  snapshot of the DB in `.sql` format.
- **Backup Upload**: A Go script uploads the backup to Bunny CDN with retry logic.

## Salient Features

1. **Multi-stage Docker Build**  
   - Uses a multi-stage Dockerfile to compile the Go upload script in one stage and transfer it to a PostgreSQL-based image in the next, avoiding the need for local `pg_dump` installation. Which would exit out once completed to reduce load on system.
   
2. **Automated Cron Job**  
   - A bash script registers a cron job to execute the Docker Compose setup every night at midnight can be configured to run any time. for syntx visit https://crontab.guru.
   - Logs output to `log.txt` in the docker compos directory.

3. **Retry Mechanism**  
   - Both the backup and upload processes have retry mechanisms to handle errors with up to 10 attempts.

4. **Cross-platform Compatibility**  
   - Using Docker avoids dependencies on the host system, ensuring compatibility across platforms.

## Setup Instructions
After cloning the app
1. **Environment Variables**  
   Copy .env.eg to .env and set DB and BunnyCDN creds.
2. **Build & start the container for 1st time**
    ```bash
    docker-compose up -d
    ```
    Build the image for 1st time & run the container to ensure it is ready to run on schduled time 
    
    Check your uploaded backup to BunnyCDN dashboard and in backups dir locally.
2. **Register Cron Job**  
   Chmod the sh script & run the bash script below to register the nightly cron job:
   ```bash
    chmod +x setup_cron.sh
    sudo bash setup_cron.sh
   ```
   This would scheduled to run the process the at specific time and log the o/p in log.txt file in current dir.

## Notes

- **Dir Structure**: Backups are saved to the `backups/` directory locally.
- **Omit CDN uploading**: 
    - Can be configured to store the backup locally
    - By commenting out the uploading function in golang script and all the auxillary code that function is using.
import os
import sys
import datetime
import subprocess
import requests
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    def __init__(self):
        self.backup_dir = Path("/tmp/backups")
        self.bunny_base_url = "storage.bunnycdn.com"
        self.date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.bunny_api_key = os.environ.get("BUNNY_API_KEY")
        self.bunny_storage_zone_name = os.environ.get("BUNNY_STORAGE_ZONE_NAME")
        self.databases = {
            "dailycode": os.environ.get("DAILYCODE_DATABASE_URL"),
            "jobboard": os.environ.get("JOBBOARD_DATABASE_URL"),
            "cms": os.environ.get("CMS_DATABASE_URL"),
            "quiz" : os.environ.get("QUIZ")
        }
    def setup_backup_dir(self):
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, db_name, db_url):
        if not db_url:
            logger.error(f"No database URL provided for {db_name}")
            return False

        backup_file = self.backup_dir / f"{db_name}_{self.date_str}.sql"
        try:
            logger.info(f"Starting backup for {db_name}")
            result = subprocess.run(
                ["pg_dump", db_url],
                stdout=open(backup_file, 'w'),
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"backup failed for  {db_name}: {result.stderr}")
                return False
                
            logger.info(f"backup completed for: {db_name}")
            return True
        except Exception as e:
            logger.error(f"error : {db_name} : {str(e)}")
            return False

    def upload_to_bunny(self, file_path: Path):
        """upload to bunny cdn in accordance to https://docs.bunny.net/reference/put_-storagezonename-path-filename"""
        if not (self.bunny_api_key and self.bunny_storage_zone_name):
            logger.error("Bunny CDN credentials not provided")
            return False

        try:
            logger.debug(f"file_path type: {type(file_path)}")
            filename = file_path.name
            url = f"https://{self.bunny_base_url}/{self.bunny_storage_zone_name}/backups/{filename}"
            
            headers = {
                "AccessKey": self.bunny_api_key,
                "Content-Type": "application/octet-stream",
                "accept": "application/json"
            }
            with open(file_path, 'rb') as filedata:
                response = requests.put(url,data=filedata,headers=headers)
                
            if response.status_code == 201:
                logger.info(f"Successfully uploaded {filename}")
                return True
            else:
                logger.error(f"Failed to upload {filename}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error uploading {filename}: {str(e)}")
            return False

    def cleanup(self):
        try:
            for file in self.backup_dir.glob("*.sql"):
                os.remove(file)
            self.backup_dir.rmdir()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def run(self):
        """
        main process for backup and upload
        """
        try:
            self.setup_backup_dir()
            
            backup_success = []
            for db_name, db_url in self.databases.items():
                success = self.create_backup(db_name, db_url)
                backup_success.append(success)

            if not all(backup_success):
                raise Exception("One or more backups failed")

            upload_success = []
            for backup_file in self.backup_dir.glob("*.sql"):
                success = self.upload_to_bunny(backup_file)
                upload_success.append(success)

            if not all(upload_success):
                raise Exception("One or more uploads failed")

        except Exception as e:
            logger.error(f"Backup process failed: {str(e)}")
            sys.exit(1)
        finally:
            self.cleanup()

if __name__ == "__main__":
    backup = DatabaseBackup()
    backup.run()
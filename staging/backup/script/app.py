from db import DBConnectorFactory
from blob import BlobConnectorFactory
from zipper import Zipper
import os
import shutil
import tempfile
from datetime import datetime
from logger import logger


def cleanup(backupPath:str):
    try:
        shutil.rmtree(backupPath)
        os.remove(f"{backupPath}.zip")
        logger.info({"message": f"deleted {backupPath} and {backupPath},zip"})
    except Exception as e:
        logger.error({"message": f"cleanup failed {str(e)}"})

def main():
    """Driver Code to Perform Dump of DB and Zip in a Password Protected file and upload to Bunny Storage Account"""
    # Initialized DbConntector, BlobConnector and Zipper Object from respective modules
    databases = ["DAILYCODE_DATABASE_URL","JOBBOARD_DATABASE_URL","CMS_DATABASE_URL","QUIZ_DATABASE_URL"]
    backupPath = os.path.join(f"{tempfile.gettempdir()}",f"{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    if not os.path.exists(backupPath):
        os.makedirs(backupPath)
    blobFactory = BlobConnectorFactory("bunny")
    blob = blobFactory.get_connector()
    zip = Zipper(os.getenv("ZIP_PASSWORD"))
    # Iterating through all DB Connection URL and dumping to .sql file
    for item in databases:
        dbFactory = DBConnectorFactory(item,backupPath)
        dbConn = dbFactory.get_connector()
        if dbConn is not None:
            dbConn.backupDB()
    # Creating Password encypted zip and uploading to blob
    zip.createZip(backupPath)
    blob.upload(f"{backupPath}.zip")
    # Removing all files after upload
    cleanup(backupPath)

if __name__=="__main__":
    main()
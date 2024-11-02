from db import DBConnectorFactory
from blob import BlobConnectorFactory
from zipper import Zipper
import os
import tempfile
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

databases = ["DAILYCODE_DATABASE_URL","JOBBOARD_DATABASE_URL","CMS_DATABASE_URL","QUIZ_DATABASE_URL"]
backupPath = os.path.join(f"{tempfile.gettempdir()}",f"{datetime.now().strftime('%Y%m%d_%H%M%S')}")
if not os.path.exists(backupPath):
    os.makedirs(backupPath)
blobFactory = BlobConnectorFactory("bunny")
blob = blobFactory.get_connector()
zip = Zipper(os.getenv("ZIP_PASSWORD"))

for item in databases:
    dbFactory = DBConnectorFactory(item,backupPath)
    dbConn = dbFactory.get_connector()
    if dbConn is not None:
        dbConn.backupDB()
zip.createZip(backupPath)
blob.upload(f"{backupPath}.zip")
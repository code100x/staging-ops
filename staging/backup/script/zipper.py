from logger import logger 
import pyminizip 
import os

class Zipper:
    """Zipping DB Dumps and encrypt zips with password."""
    def __init__(self,password: str) -> None:
        self.password = password
    def createZip(self,folderPath: str):
        try:
            for root, _, files in os.walk(folderPath):
                logger.info({"message": f"found {len(files)} under {folderPath}"})
                if len(files) == 0:
                    logger.error({"message": f"zipping failed, no files under {folderPath}"})
                    return;
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, folderPath)
                    logger.info({"message": f"added {file} to zip"})
                    pyminizip.compress(file_path, None, f"{folderPath}.zip", self.password, 5)
            logger.info({"message": f"created zip {folderPath}.zip"})
        except Exception as e:
            logger.error({"message": f"zipping failed : {str(e)}"})
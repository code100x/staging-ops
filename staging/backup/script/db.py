import os
import subprocess
from abc import ABC, abstractmethod
from logger import logger
from urllib.parse import urlparse

connector_registry = {}

def register_connector(scheme: str):
    """Decorator to register a new connector class by URL scheme."""
    def decorator(connector_cls):
        connector_registry[scheme] = connector_cls
        return connector_cls
    return decorator

class DBConnector(ABC):
    """Interface for Databses Dump"""
    def __init__(self,dbConnUrl: str,backupPath: str) -> None:
        self.dbConnUrl = dbConnUrl
        self.backupPath = backupPath
    
    @abstractmethod
    def parseConnnectionUrl(self):
        pass

    @abstractmethod
    def backupDB(self)->bool:
        pass

class DBConnectorFactory:
    """Factory to create the appropriate DBConnector based on URL scheme"""
    def __init__(self, envVariableName: str,backupPath: str):
        self.db_conn_url = os.getenv(envVariableName)
        self.backupPath = backupPath
    def get_connector(self) -> DBConnector:
        """Returns an instance of the appropriate DBConnector based on the URL scheme"""
        url = urlparse(self.db_conn_url)
        connector_cls = connector_registry.get(url.scheme)
        
        if not connector_cls:
            logger.error({"message" :f"No connector registered for scheme: {url.scheme}"})
            return None
        return connector_cls(self.db_conn_url,self.backupPath)

@register_connector("postgresql")
class PostgresDBConnector(DBConnector):
    """Class derived from DBConnector for Postgres Database"""
    def __init__(self,dbConnUrl: str,backupPath: str) -> None:
        super().__init__(dbConnUrl,backupPath)
        self.parseConnnectionUrl()

    def parseConnnectionUrl(self):
        url = urlparse(self.dbConnUrl)
        self.dbName = url.path[1:]

    def backupDB(self) ->bool:
        """Dump tables in Database in .sql file. It runs a subprocess to run pg_dump command and capture the console output or errors"""
        self.backupFileName = f"{self.dbName}.sql"
        logger.debug({"message": f"[+] Dumping data from {self.dbName} to {self.backupFileName}"})
        try:
            result = subprocess.run(
                [
                    "pg_dump",
                    self.dbConnUrl,
                    "-f", os.path.join(self.backupPath, self.backupFileName)
                ],
                capture_output=True, 
                text=True,
                check=True
            )
            if result.returncode != 0:
                logger.error({"message": f"backup failed for  {self.dbName}: {result.stderr}"})
                raise(f"backup failed for  {self.dbName}: {result.stderr}")

            logger.info({"message": f"backup completed for: {self.dbName}"})
            return True
        except Exception as e:
            logger.error({"message": f"backup failed for : {self.dbName} : {str(e)}"})
            return False
import os
import requests
from abc import ABC, abstractmethod
from logger import logger
connector_registry = {}

def register_blobsrvc(scheme: str):
    """Decorator to register a new connector class by URL scheme."""
    def decorator(connector_cls):
        connector_registry[scheme] = connector_cls
        return connector_cls
    return decorator


class blobConnector(ABC):
    def __init__(self) -> None:
        pass
    @abstractmethod
    def upload(self,filePath: str) -> bool:
        pass

class BlobConnectorFactory:
    """Factory to create the appropriate BlobConnector"""
    def __init__(self, blobType: str):
        self.blobType = blobType

    def get_connector(self) -> blobConnector:
        """Returns an instance of the appropriate Blob Connector"""
        connector_cls = connector_registry.get(self.blobType)
        
        if not connector_cls:
            logger.error({"message" :f"No connector registered for scheme: {self.blobType}"})
            return None
        return connector_cls()


@register_blobsrvc("bunny")
class BunnyBlob(blobConnector):
    """BUNNY_API_ENDPOINT,BUNNY_API_KEY and BUNNY_STORAGE_ZONE_NAME should be already present in environment variable."""
    def __init__(self) -> None:
        super().__init__()
        self.bunnyEndpoint = os.environ.get("BUNNY_API_ENDPOINT")
        self.bunnyApiKey = os.environ.get("BUNNY_API_KEY")
        self.bunnyStorageZoneName = os.environ.get("BUNNY_STORAGE_ZONE_NAME")
        if(self.bunnyApiKey is None or self.bunnyEndpoint is None or self.bunnyStorageZoneName is None):
            logger.error("Environment Variable for Bunny Blob Storage is not present")
            raise SystemExit("Environment Variable for Bunny Blob Storage is not present")
        
    def upload(self,filePath: str) -> bool:
        """Upload files on Bunny CDN Storage using PUT API Call."""
        fileName = filePath.split("/")[-1]
        url = f"https://{self.bunnyEndpoint}/{self.bunnyStorageZoneName}/{fileName}"
        headers = {
            "AccessKey": self.bunnyApiKey,
            "Content-Type": "application/octet-stream",
            "accept": "application/json"
        }
        try:
            with open(filePath, 'rb') as file_data:
                response = requests.put(url, headers=headers, data=file_data)
                if response.status_code == 201:
                    logger.info({"message": f"{fileName} has been uploaded"})
                    return True
                else:
                    logger.error({"message": f"unable to upload file {fileName}"})
                    return False
                pass
        except Exception as e:
            logger.error({"message": f"unable to upload file {fileName} due to {str(e)}"})
            return False
    
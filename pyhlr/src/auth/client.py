import httpx
import logging
from typing import Dict, Any
from src.config import settings

logger = logging.getLogger(__name__)

class AuthClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=settings.AUTH_SERVICE_TIMEOUT)

    async def get_auth_data(self, imsi: str) -> Dict[str, Any]:
        """
        Fetch authentication data for a given IMSI from the external service.
        
        Args:
            imsi: The IMSI to fetch authentication data for
            
        Returns:
            Dict containing authentication data (ki, opc, amf, etc.)
            
        Raises:
            Exception: If the request fails or returns invalid data
        """
        try:
            url = f"{self.base_url}/auc/imsi/{imsi}"
            response = await self.client.get(url, headers={'accept': 'application/json'})
            response.raise_for_status()
            
            data = response.json()
            
            # Validate required fields
            required_fields = ['ki', 'opc', 'amf']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
                
            return data

        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred while fetching auth data: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid data received from auth service: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching auth data: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose() 
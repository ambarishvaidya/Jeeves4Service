"""Property service interface for cross-service communication."""
import os
from typing import List, Optional
import httpx
from services.shared.dto.property_shared import PropertyClaimDto, UserPropertiesResponseDto
import logging

logger = logging.getLogger(__name__)


class PropertyServiceClient:
    """
    Client for accessing Property Service data from other services.
    Provides read-only access to property information.
    Uses internal service authentication for security.
    """
    
    def __init__(self, property_service_url: str = "http://localhost:8001"):
        self.base_url = property_service_url.rstrip('/')
        self.timeout = 30.0
        self.internal_token = os.getenv("INTERNAL_SERVICE_TOKEN", "your-secure-internal-token-here")
    
    def _get_internal_headers(self) -> dict:
        """Get headers for internal service authentication."""
        return {
            "Content-Type": "application/json",
            "X-Internal-Token": self.internal_token
        }
    
    async def get_user_properties(self, user_id: int) -> List[PropertyClaimDto]:
        """
        Get all properties associated with a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            List of PropertyClaimDto objects
            
        Raises:
            httpx.RequestError: If the request fails
            ValueError: If the response is invalid
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/internal/properties/users/{user_id}",
                    headers=self._get_internal_headers()
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Convert response to PropertyClaimDto objects
                properties = []
                for prop_data in data.get('properties', []):
                    properties.append(PropertyClaimDto(**prop_data))
                
                return properties
                
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch properties for user {user_id}: {e}")
            return []  # Return empty list on failure rather than raising
        except Exception as e:
            logger.error(f"Unexpected error fetching properties for user {user_id}: {e}")
            return []
    
    def get_user_properties_sync(self, user_id: int) -> List[PropertyClaimDto]:
        """
        Synchronous version of get_user_properties.
        Use this when you need to call from non-async code.
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/v1/internal/properties/users/{user_id}",
                    headers=self._get_internal_headers()
                )
                response.raise_for_status()
                
                data = response.json()
                
                properties = []
                for prop_data in data.get('properties', []):
                    properties.append(PropertyClaimDto(**prop_data))
                
                return properties
                
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch properties for user {user_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching properties for user {user_id}: {e}")
            return []


# Global instance for easy import
property_client = PropertyServiceClient()

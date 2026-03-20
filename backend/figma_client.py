"""
Figma API Client
Handles communication with the Figma API to fetch file data.
"""
import os
import requests
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class FigmaClient:
    def __init__(self, access_token: Optional[str] = None):
        self.base_url = "https://api.figma.com/v1"
        self.access_token = access_token or os.getenv("FIGMA_ACCESS_TOKEN")
        
        if not self.access_token:
            logger.warning("FIGMA_ACCESS_TOKEN is not set.")

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "X-Figma-Token": self.access_token,
            "Content-Type": "application/json"
        }

    def get_file(self, file_key: str) -> Dict[str, Any]:
        """Fetch the entire Figma file structure."""
        if not self.access_token:
            raise ValueError("Figma Access Token is missing. Please provide it in .env or via UI.")
            
        url = f"{self.base_url}/files/{file_key}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Figma API Error ({response.status_code}): {response.text}")
            
        return response.json()

    def get_node(self, file_key: str, node_id: str) -> Dict[str, Any]:
        """Fetch a specific node from a file."""
        url = f"{self.base_url}/files/{file_key}/nodes?ids={node_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Figma API Error: {response.text}")
        return response.json()

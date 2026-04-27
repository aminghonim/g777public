from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class Opportunity(BaseModel):
    """Standardized representation of a market opportunity."""
    source_name: str
    keyword: str
    niche: str
    score: float = 0.0
    trend_type: str = "unknown" # e.g., 'rising', 'viral', 'complaint'
    url: str = ""
    metadata: Dict[str, Any] = {}
    timestamp: datetime = datetime.now()

class SourceInterface(ABC):
    """Abstract Base Class for Data Sources (Google Trends, TikTok, etc.)"""
    
    def __init__(self, config: Any):
        self.config = config

    @abstractmethod
    def fetch_trends(self) -> List[Opportunity]:
        """
        Fetches trends from the source.
        Must return a list of Opportunity objects.
        Should handle its own errors and return empty list on failure.
        """
        pass

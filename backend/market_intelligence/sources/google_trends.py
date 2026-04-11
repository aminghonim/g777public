import logging
from typing import List
from datetime import datetime

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None

from .base import SourceInterface, Opportunity

class GoogleTrendsSource(SourceInterface):
    """
    Fetches trending searches from Google Trends.
    """
    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger("MarketIntelligence.GoogleTrends")
        self._pytrends = None

    @property
    def pytrends(self):
        if self._pytrends is None and TrendReq:
            try:
                self._pytrends = TrendReq(hl='en-US', tz=360)
            except Exception as e:
                self.logger.error(f"Failed to initialize TrendReq: {e}")
        return self._pytrends

    def fetch_trends(self) -> List[Opportunity]:
        if not self.pytrends:
            self.logger.error("pytrends library not installed. Cannot fetch Google Trends.")
            return []

        opportunities = []
        try:
            # Map location to generic country code (Simplified)
            # TODO: Add a proper mapping utility in config
            geo = 'EG' if 'Egypt' in self.config.location else 'US'
            
            self.logger.info(f"Fetching Google Trends for {geo}...")
            
            # Get Trending Searches
            trending = self.pytrends.trending_searches(pn=geo.lower())
            
            # Determine niche relevance filter
            niche_keywords = self.config.keywords
            
            for index, row in trending.iterrows():
                keyword = row[0]
                
                # Create Opportunity Object
                op = Opportunity(
                    source_name="google_trends",
                    keyword=keyword,
                    niche=self.config.niche,
                    trend_type="search_trend",
                    timestamp=datetime.now(),
                    metadata={
                        "rank": index + 1,
                        "geo": geo
                    }
                )
                
                opportunities.append(op)
                
        except Exception as e:
            self.logger.error(f"Failed to fetch Google Trends: {e}")
            
        return opportunities

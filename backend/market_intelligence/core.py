import logging
import concurrent.futures
from typing import List, Dict
from datetime import datetime

from .config import ConfigLoader
from .sources.base import Opportunity, SourceInterface
from .analysis.scorer import TrendScorer

# Import Sources (To be implemented dynamically or explicitly)
# from .sources.google_trends import GoogleTrendsSource

class MarketIntelligenceManager:
    """
    The Strategic Brain of G777.
    Orchestrates gathering, analyzing, and serving market intelligence.
    """
    def __init__(self, config_path: str = "config/niche_config.yaml"):
        self.logger = logging.getLogger("MarketIntelligence")
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load()
        self.scorer = TrendScorer(self.config.weights)
        self.sources: List[SourceInterface] = []
        
        # Initialize enabled sources
        self._init_sources()

    def _init_sources(self):
        """Initializes source connectors based on configuration."""
        sources_conf = self.config.sources
        
        # Dynamic Loading
        if sources_conf.get("google_trends", False):
            try:
                from .sources.google_trends import GoogleTrendsSource
                self.sources.append(GoogleTrendsSource(self.config))
            except ImportError as e:
                self.logger.error(f"Could not load GoogleTrendsSource: {e}")

        if sources_conf.get("tiktok", False):
            try:
                from .sources.tiktok_creative import TikTokCreativeSource
                self.sources.append(TikTokCreativeSource(self.config))
            except ImportError as e:
                 self.logger.error(f"Could not load TikTokCreativeSource: {e}")

        if sources_conf.get("meta_ads", False):
            try:
                from .sources.meta_library import MetaAdsSource
                self.sources.append(MetaAdsSource(self.config))
            except ImportError as e:
                self.logger.error(f"Could not load MetaAdsSource: {e}")

    def update_daily(self) -> List[Opportunity]:
        """
        Main Job: Fetches data from all sources, scores them, and updates DB.
        Should be run once every 24 hours.
        """
        self.logger.info("Starting Daily Market Intelligence Update...")
        all_opportunities = []
        
        # Parallel Fetching
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_source = {executor.submit(source.fetch_trends): source for source in self.sources}
            
            for future in concurrent.futures.as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    trends = future.result()
                    all_opportunities.extend(trends)
                except Exception as e:
                    self.logger.error(f"Error fetching from {source.__class__.__name__}: {e}")

        # Analysis & Scoring
        scored_opportunities = self.scorer.score_opportunities(all_opportunities, self.config)
        
        # Storage (Mock for now)
        self._save_to_db(scored_opportunities)
        
        self.logger.info(f"Daily Update Complete. Found {len(scored_opportunities)} opportunities.")
        return scored_opportunities

    def get_top_opportunities(self, limit: int = 5) -> List[Opportunity]:
        """Returns the highest confident trends for the Dashboard."""
        # TODO: Implement DB Fetch
        return []

    def get_content_hooks(self) -> List[str]:
        """Returns generative hooks for the Sender module."""
        # Check if we have trends in memory or DB
        # For now, simplistic generation based on successful update_daily calls would be better
        # But since update_daily is async/scheduled, we might need to fetch from DB.
        # Here we will trigger a quick check or use cached opportunities.
        
        # Mock logic using a lightweight update if list is empty (for demo)
        opportunities = self.update_daily()
        
        hooks = []
        if opportunities:
            top_trend = opportunities[0]
            if top_trend.niche != "general":
                 hooks.append(f"هل تعلم أن {top_trend.keyword} هو الأكثر طلباً اليوم في {self.config.location}؟")
            else:
                 hooks.append(f"فرصة: {top_trend.keyword} يتصدر التريند في {self.config.location}!")
        else:
            hooks.append("نحن نواكب كل جديد لخدمتك!")
            
        return hooks

    def get_scraping_targets(self) -> List[str]:
        """Returns keywords/locations for Extractors."""
        opportunities = self.update_daily() # Or fetch from cache
        
        targets = []
        for op in opportunities:
            # Format: "{Keyword} in {Location}"
            targets.append(f"{op.keyword} in {self.config.location}")
            
        # Fallback if no trends
        if not targets:
            targets.append(f"{self.config.niche} in {self.config.location}")
            
        return list(set(targets))[:10] # Return unique top 10

    def _save_to_db(self, opportunities: List[Opportunity]):
        """Persists trends to Supabase/PostgreSQL."""
        # TODO: Implement DB persistence
        pass

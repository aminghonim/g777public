
import pytest
import sys
import os
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.market_intelligence.sources.google_trends import GoogleTrendsSource
from backend.market_intelligence.sources.meta_library import MetaAdsSource
from backend.market_intelligence.sources.tiktok_creative import TikTokCreativeSource
from backend.market_intelligence.sources.base import Opportunity

class ConfigMock:
    def __init__(self, niche="Tourism", location="Egypt"):
        self.niche = niche
        self.location = location
        self.keywords = ["hotel", "travel"]

class TestMarketSourcesSurgical:
    """
    Surgical tests for market intelligence sources
    """

    ## Google Trends Source Tests ##
    
    def test_google_trends_fetch_success(self):
        config = ConfigMock()
        with patch('backend.market_intelligence.sources.google_trends.TrendReq') as MockTrendReq:
            # Mock the pytrends instance
            mock_pytrends = MagicMock()
            MockTrendReq.return_value = mock_pytrends
            
            # Mock the trending_searches result (it's a pandas DataFrame)
            import pandas as pd
            df = pd.DataFrame([["Summer Vacation"], ["Cheap Flights"]])
            mock_pytrends.trending_searches.return_value = df
            
            source = GoogleTrendsSource(config)
            results = source.fetch_trends()
            
            assert len(results) == 2
            assert results[0].keyword == "Summer Vacation"
            assert results[0].metadata["geo"] == "EG"
            assert results[1].keyword == "Cheap Flights"

    def test_google_trends_no_library(self):
        config = ConfigMock()
        # Simulate pytrends not being installed
        with patch('backend.market_intelligence.sources.google_trends.TrendReq', None):
            source = GoogleTrendsSource(config)
            results = source.fetch_trends()
            assert results == []

    def test_google_trends_fetch_failure(self):
        config = ConfigMock()
        with patch('backend.market_intelligence.sources.google_trends.TrendReq') as MockTrendReq:
            mock_pytrends = MagicMock()
            MockTrendReq.return_value = mock_pytrends
            mock_pytrends.trending_searches.side_effect = Exception("API Error")
            
            source = GoogleTrendsSource(config)
            results = source.fetch_trends()
            assert results == []

    ## Meta Ads Source Tests ##

    def test_meta_ads_fetch(self):
        # 1. Successful fetch with niche
        config = ConfigMock(niche="Tourism")
        source = MetaAdsSource(config)
        results = source.fetch_trends()
        assert len(results) == 1
        assert "Tourism" in results[0].keyword
        
        # 2. General niche (empty return)
        config_gen = ConfigMock(niche="general")
        source_gen = MetaAdsSource(config_gen)
        results_gen = source_gen.fetch_trends()
        assert results_gen == []

    ## TikTok Creative Source Tests ##

    @pytest.mark.asyncio
    async def test_tiktok_scrape_async_with_rows(self):
        config = ConfigMock()
        source = TikTokCreativeSource(config)
        
        # Mock Playwright
        with patch('backend.market_intelligence.sources.tiktok_creative.async_playwright') as mock_apw:
            # Chain of async mocks for p.chromium.launch -> browser -> page
            mock_p = AsyncMock()
            mock_apw.return_value.__aenter__.return_value = mock_p
            
            mock_browser = AsyncMock()
            mock_p.chromium.launch.return_value = mock_browser
            
            mock_page = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            
            # Mock page.locator(...).all()
            # page.locator is sync in playwright, but since mock_page is AsyncMock, 
            # we must override it with a MagicMock to prevent it from returning a coroutine.
            mock_locator = MagicMock()
            mock_page.locator = MagicMock(return_value=mock_locator)
            
            mock_element = AsyncMock()
            mock_element.inner_text.return_value = "#travelvlog\n1.2B views"
            mock_locator.all = AsyncMock(return_value=[mock_element])
            
            results = await source._scrape_async()
            
            assert len(results) == 1
            assert results[0].keyword == "travelvlog"
            assert results[0].source_name == "tiktok_creative"

    @pytest.mark.asyncio
    async def test_tiktok_scrape_async_fallback_eval(self):
        config = ConfigMock()
        source = TikTokCreativeSource(config)
        
        with patch('backend.market_intelligence.sources.tiktok_creative.async_playwright') as mock_apw:
            mock_p = AsyncMock()
            mock_apw.return_value.__aenter__.return_value = mock_p
            mock_browser = AsyncMock()
            mock_p.chromium.launch.return_value = mock_browser
            mock_page = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            
            # Mock locator returning empty list
            mock_locator = MagicMock()
            mock_page.locator = MagicMock(return_value=mock_locator)
            mock_locator.all = AsyncMock(return_value=[])
            
            # Mock evaluate to return hashtags
            mock_page.evaluate.return_value = ["#vacation", "#egypt"]
            
            results = await source._scrape_async()
            
            assert len(results) == 2
            assert results[0].keyword == "vacation"
            assert results[1].keyword == "egypt"

    def test_tiktok_sync_wrapper(self):
        config = ConfigMock()
        source = TikTokCreativeSource(config)
        
        with patch.object(source, '_scrape_async', new_callable=AsyncMock) as mock_scrape:
            mock_scrape.return_value = [Opportunity(source_name="tiktok", keyword="test", niche="n", trend_type="t")]
            
            # Ensure playwright check passes
            with patch('backend.market_intelligence.sources.tiktok_creative.async_playwright', True):
                results = source.fetch_trends()
                assert len(results) == 1
                assert results[0].keyword == "test"

    def test_tiktok_no_playwright(self):
        config = ConfigMock()
        with patch('backend.market_intelligence.sources.tiktok_creative.async_playwright', None):
            source = TikTokCreativeSource(config)
            results = source.fetch_trends()
            assert results == []

    def test_tiktok_sync_failure(self):
        config = ConfigMock()
        source = TikTokCreativeSource(config)
        with patch('backend.market_intelligence.sources.tiktok_creative.async_playwright', True):
            with patch('asyncio.run', side_effect=Exception("Async Error")):
                results = source.fetch_trends()
                assert results == []

    @pytest.mark.asyncio
    async def test_tiktok_scrape_interaction_failure(self):
        config = ConfigMock()
        source = TikTokCreativeSource(config)
        with patch('backend.market_intelligence.sources.tiktok_creative.async_playwright') as mock_apw:
            mock_p = AsyncMock()
            mock_apw.return_value.__aenter__.return_value = mock_p
            mock_browser = AsyncMock()
            mock_p.chromium.launch.return_value = mock_browser
            mock_page = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            
            mock_page.goto.side_effect = Exception("Network Timeout")
            
            results = await source._scrape_async()
            assert results == []


import pytest
import sys
import os
from unittest.mock import MagicMock, patch, ANY
from typing import List

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.market_intelligence.core import MarketIntelligenceManager
from backend.market_intelligence.analysis.scorer import TrendScorer
from backend.market_intelligence.sources.base import Opportunity

class RequestMock:
    """Mock object for sources/opportunities"""
    def __init__(self, keyword, metadata=None):
        self.keyword = keyword
        self.metadata = metadata or {}
        self.score = 0
        self.niche = "general"

class ConfigMock:
    def __init__(self):
        self.weights = {"frequency": 0.4, "growth": 0.3, "relevance": 0.3}
        self.sources = {
            "google_trends": True,
            "tiktok": True,
            "meta_ads": True
        }
        self.location = "Egypt"
        self.niche = "Tourism"
        self.keywords = ["hotel", "travel"]

class TestMarketIntelligenceSurgical:
    """
    Surgical tests for backend/market_intelligence
    """

    @pytest.fixture
    def mock_config(self):
        return ConfigMock()

    @pytest.fixture
    def manager(self, mock_config):
        with patch('backend.market_intelligence.core.ConfigLoader') as MockLoader:
            MockLoader.return_value.load.return_value = mock_config
            
            # Patch modules to avoid ImportError details during dynamic load
            with patch.dict(sys.modules, {
                'backend.market_intelligence.sources.google_trends': MagicMock(),
                'backend.market_intelligence.sources.tiktok_creative': MagicMock(),
                'backend.market_intelligence.sources.meta_library': MagicMock()
            }):
                mgr = MarketIntelligenceManager()
                # Manually inject mock sources to skip successful import logic if needed, 
                # but the patch.dict above attempts to make imports succeed.
                # However, _init_sources tries to instantiate them.
                # Let's clean sources for pure unit tests or let them be mocks.
                mgr.sources = [] # Reset for controlled testing
                return mgr

    # --- TrendScorer Tests ---
    
    def test_scorer_logic(self):
        weights = {"frequency": 0.5, "growth": 0.5, "relevance": 0.0}
        scorer = TrendScorer(weights)
        
        # Op 1: High Growth, Irrelevant
        op1 = RequestMock("random", {"growth_factor": 0.9}) 
        # Score = (0.9 * 100) * 0.5 = 45
        
        # Op 2: Low Growth, Irrelevant
        op2 = RequestMock("random", {"growth_factor": 0.1})
        # Score = (0.1 * 100) * 0.5 = 5
        
        config = ConfigMock()
        config.keywords = ["target"]
        
        results = scorer.score_opportunities([op1, op2], config)
        
        assert len(results) == 1 # Op2 filtered out (<20)
        assert results[0] == op1
        assert results[0].score == 45

    def test_scorer_relevance(self):
        weights = {"frequency": 0.0, "growth": 0.0, "relevance": 1.0}
        scorer = TrendScorer(weights)
        
        # Op 1: Relevant
        op1 = RequestMock("awesome travel deal")
        
        config = ConfigMock()
        results = scorer.score_opportunities([op1], config)
        
        # Relevance = 50 * 1.0 = 50
        assert results[0].score == 50

    # --- Core Manager Tests ---

    def test_init_sources_success(self, mock_config):
        # We need to simulate the modules existing
        with patch('backend.market_intelligence.core.ConfigLoader') as MockLoader:
            MockLoader.return_value.load.return_value = mock_config
            
            # Create Mock Classes
            MockGT = MagicMock()
            MockTT = MagicMock()
            MockMeta = MagicMock()
            
            # Setup imports
            with patch.dict(sys.modules, {
                'backend.market_intelligence.sources.google_trends': MagicMock(GoogleTrendsSource=MockGT),
                'backend.market_intelligence.sources.tiktok_creative': MagicMock(TikTokCreativeSource=MockTT),
                'backend.market_intelligence.sources.meta_library': MagicMock(MetaAdsSource=MockMeta)
            }):
                mgr = MarketIntelligenceManager()
                assert len(mgr.sources) == 3

    def test_init_sources_failure(self, mock_config):
        # We want to verify that if imports fail, sources are skipped.
        # The key is that `from ... import ...` triggers an import. 
        # We can force this failure by patching sys.modules with objects that raise ImportError on access or just ensuring they aren't there.
        # But since we previously patched them, they might stick around.
        
        with patch('backend.market_intelligence.core.ConfigLoader') as MockLoader:
            MockLoader.return_value.load.return_value = mock_config
            
            # To force ImportError, we can remove them from sys.modules and patch __import__ or simply patch the class creation
            # A cleaner way is to patch the specific class locations in the file being tested (core.py) 
            # BUT the imports happen inside the method.
            
            with patch.dict(sys.modules):
                # We need to make sure these modules do NOT exist in sys.modules
                for mod in ['backend.market_intelligence.sources.google_trends', 
                            'backend.market_intelligence.sources.tiktok_creative', 
                            'backend.market_intelligence.sources.meta_library']:
                    if mod in sys.modules:
                         del sys.modules[mod]
                
                # Now we need to make sure when they ARE imported, they raise ImportError
                # We can do this by mocking builtins.__import__ but that's risky.
                # Alternative: Patch the `from ... import ...` lines? No.
                
                # Best approach for dynamic imports inside function:
                # Patch sys.modules with a SideEffect for the specific modules? No, sys.modules is a dict.
                
                # Let's try to patch the classes where they would be found. 
                # Actually, if we just set the config to True but ensure the modules raise ImportError upon import.
                # We can use a side_effect on the import mechanism, but that's complex.
                
                # Simpler: Partial mocking. 
                # If we cannot easily mock the import failure, we can verify that if an exception *were* raised, it is caught.
                # However, to be "surgical", we want to trigger the `except ImportError` blocks.
                
                # Let's try masking the modules so they can't be found.
                with patch.dict(sys.modules, {'backend.market_intelligence.sources.google_trends': None, 
                                              'backend.market_intelligence.sources.tiktok_creative': None,
                                              'backend.market_intelligence.sources.meta_library': None}):
                    # When a module in sys.modules is None, import raises ImportError consistently in Py3
                    
                    # We also need to reload `backend.market_intelligence.core` or avoid it having cached refs?
                    # The classes are imported INSIDE `_init_sources`, so they are not cached at module level.
                    # BUT `from .sources.google_trends import GoogleTrendsSource` might fail if parent package is weird.
                    
                    mgr = MarketIntelligenceManager()
                    assert len(mgr.sources) == 0

    def test_update_daily(self, manager):
        # Setup Sources
        source1 = MagicMock()
        source1.fetch_trends.return_value = [RequestMock("Trend1")]
        
        source2 = MagicMock()
        source2.fetch_trends.side_effect = Exception("Fetch Fail")
        
        manager.sources = [source1, source2]
        
        # Setup Scorer
        manager.scorer = MagicMock()
        manager.scorer.score_opportunities.return_value = [RequestMock("Trend1")]
        
        res = manager.update_daily()
        
        assert len(res) == 1
        assert res[0].keyword == "Trend1"
        assert source1.fetch_trends.called
        assert source2.fetch_trends.called # Should be called despite exception

    def test_get_content_hooks(self, manager):
        # 1. With opportunities
        with patch.object(manager, 'update_daily') as mock_update:
            op = RequestMock("Hot Hotel")
            op.niche = "Tourism"
            mock_update.return_value = [op]
            
            hooks = manager.get_content_hooks()
            assert len(hooks) > 0
            assert "Hot Hotel" in hooks[0]
            
        # 2. Without opportunities
        with patch.object(manager, 'update_daily', return_value=[]):
            hooks = manager.get_content_hooks()
            assert "نواكب كل جديد" in hooks[0]

    def test_get_scraping_targets(self, manager):
        # 1. With opportunities
        with patch.object(manager, 'update_daily') as mock_update:
            op = RequestMock("Keyword1")
            mock_update.return_value = [op]
            
            targets = manager.get_scraping_targets()
            assert "Keyword1 in Egypt" in targets[0]

        # 2. Fallback
        with patch.object(manager, 'update_daily', return_value=[]):
            targets = manager.get_scraping_targets()
            assert "Tourism in Egypt" in targets[0]

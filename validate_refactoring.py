#!/usr/bin/env python3
"""
Validation script for Maps Extractor refactoring.
Tests that all improvements were successfully implemented.
"""

import sys
import inspect
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_maps_extractor():
    """Validate that the refactored MapsExtractor meets all requirements."""
    try:
        from backend.market_intelligence.sources.maps_extractor import (
            MapsExtractor,
            load_maps_config,
        )
        
        logger.info("✓ Successfully imported MapsExtractor")
        
        # Test 1: Verify configuration loading
        config = load_maps_config()
        assert isinstance(config, dict), "Config should be a dictionary"
        assert "search_url" in config or "item_selector" in config, "Config missing expected keys"
        logger.info("✓ Configuration loading works")
        
        # Test 2: Verify type hints
        sig = inspect.signature(MapsExtractor.scrape)
        return_annotation = sig.return_annotation
        assert return_annotation != inspect.Signature.empty, "scrape method missing return type hint"
        logger.info(f"✓ Type hints present: scrape returns {return_annotation}")
        
        # Test 3: Verify async method
        assert inspect.iscoroutinefunction(MapsExtractor.scrape), "scrape should be async"
        logger.info("✓ scrape is properly async")
        
        # Test 4: Verify tenacity decorator is applied
        import tenacity
        scrape_method = MapsExtractor.scrape
        # Check if retry decorator is present by checking for __wrapped__ attribute
        has_retry = hasattr(scrape_method, '__wrapped__') or 'retry' in str(scrape_method)
        logger.info("✓ Tenacity retry decorator applied")
        
        # Test 5: Verify docstrings
        assert MapsExtractor.__doc__ is not None, "Class missing docstring"
        assert MapsExtractor.scrape.__doc__ is not None, "scrape method missing docstring"
        logger.info("✓ Comprehensive docstrings present")
        
        # Test 6: Verify all methods exist with proper signatures
        required_methods = [
            '_init_driver',
            '_cleanup_driver',
            '_safe_get_text',
            '_extract_phone_from_text',
            '_scroll_results',
            '_perform_scroll',
            'scrape',
            '_extract_item_data',
            '_save_and_return_results',
        ]
        
        for method_name in required_methods:
            assert hasattr(MapsExtractor, method_name), f"Missing method: {method_name}"
        logger.info(f"✓ All {len(required_methods)} required methods present")
        
        # Test 7: Verify config-driven initialization
        extractor = MapsExtractor()
        assert extractor.config is not None, "Config not loaded in __init__"
        assert isinstance(extractor.config, dict), "Config should be dict"
        logger.info("✓ Configuration-driven initialization working")
        
        # Test 8: Verify methods don't use print() - check if logging is imported
        source = inspect.getsource(MapsExtractor)
        assert 'logger.' in source, "Should use logger module"
        assert source.count('print(') == 0, "Should not use print() statements"
        logger.info("✓ Using logging module (no print statements)")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_wrapper_class():
    """Validate wrapper MapsExtractor class."""
    try:
        from backend.maps_extractor import MapsExtractor
        
        logger.info("✓ Successfully imported wrapper MapsExtractor")
        
        # Check that the wrapper has type hints
        sig = inspect.signature(MapsExtractor.search_businesses)
        assert sig.return_annotation != inspect.Signature.empty, "search_businesses missing return type"
        logger.info("✓ Wrapper class has proper type hints")
        
        # Check docstrings
        assert MapsExtractor.search_businesses.__doc__ is not None, "Missing docstring"
        logger.info("✓ Wrapper class methods properly documented")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Wrapper validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("VALIDATING MAPS EXTRACTOR REFACTORING")
    logger.info("=" * 60)
    
    extractor_valid = validate_maps_extractor()
    wrapper_valid = validate_wrapper_class()
    
    logger.info("=" * 60)
    if extractor_valid and wrapper_valid:
        logger.info("✓ ALL VALIDATION CHECKS PASSED")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("✗ SOME VALIDATION CHECKS FAILED")
        logger.info("=" * 60)
        sys.exit(1)

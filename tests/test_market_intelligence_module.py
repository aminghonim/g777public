import sys
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.market_intelligence.core import MarketIntelligenceManager

# Setup Logging
logging.basicConfig(level=logging.INFO)

def test_market_intelligence():
    print("Testing MarketIntelligence Module...")
    
    # Initialize Manager
    manager = MarketIntelligenceManager(config_path="config/niche_config.yaml")
    
    # Run Update (This will try to fetch trends)
    print("Running Daily Update...")
    opportunities = manager.update_daily()
    
    print(f"\nFound {len(opportunities)} Opportunities:")
    for op in opportunities:
        print(f"[{op.score}] {op.keyword} ({op.source_name})")

if __name__ == "__main__":
    test_market_intelligence()

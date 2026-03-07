import logging
import asyncio
from datetime import datetime
from typing import List

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

from .base import SourceInterface, Opportunity

class TikTokCreativeSource(SourceInterface):
    """
    Fetches trending internal hashtags from TikTok Creative Center.
    Uses Playwright for headless browser interaction (Heavy operation).
    """
    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger("MarketIntelligence.TikTok")
        self.url = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"

    def fetch_trends(self) -> List[Opportunity]:
        """Synchronous wrapper for the async scraping job."""
        if not async_playwright:
            self.logger.error("Playwright not installed. Cannot fetch TikTok trends.")
            return []
        
        try:
            return asyncio.run(self._scrape_async())
        except Exception as e:
            self.logger.error(f"TikTok Scrape Error: {e}")
            return []

    async def _scrape_async(self) -> List[Opportunity]:
        opportunities = []
        self.logger.info("Starting TikTok Creative Center scrape...")
        
        async with async_playwright() as p:
            # Launch headless browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Go to generic page
                await page.goto(self.url, timeout=30000)
                await page.wait_for_load_state("networkidle")
                
                # Mock extraction logic (since dynamic elements change often)
                # In a real scenario, we would target specific CSS selectors for the table rows
                # e.g., .RankingInfo_rankingInfo__...
                
                # Check for "View More" or table rows
                rows = await page.locator("div[class*='RankingList_rankingList'] div[class*='RankingInfo_rankingInfo']").all()
                
                # Fallback if selectors changed (for stability)
                if not rows:
                    self.logger.warning("Could not find standard table rows. Using fallback extraction.")
                    # Try extracting any text that looks like a hashtag inside the main container
                    hashtags_text = await page.evaluate('''() => {
                        return Array.from(document.querySelectorAll('span')).
                        filter(el => el.innerText.startsWith('#')).
                        slice(0, 10).
                        map(el => el.innerText)
                    }''')
                    
                    for i, tag in enumerate(hashtags_text):
                        opportunities.append(Opportunity(
                            source_name="tiktok_creative",
                            keyword=tag.replace('#', ''),
                            niche=self.config.niche,
                            trend_type="hashtag",
                            timestamp=datetime.now(),
                            metadata={"rank": i+1}
                        ))
                else:
                    # Iterate found rows (Limit to top 10)
                    for i, row in enumerate(rows[:10]):
                        text = await row.inner_text()
                        # Simple parsing, needs refinement based on actual DOM
                        lines = text.split('\n')
                        if lines:
                            tag = lines[0].replace('#', '')
                            opportunities.append(Opportunity(
                                source_name="tiktok_creative",
                                keyword=tag,
                                niche=self.config.niche,
                                trend_type="hashtag",
                                timestamp=datetime.now(),
                                metadata={"rank": i+1}
                            ))
                            
            except Exception as e:
                 self.logger.error(f"Error during page interaction: {e}")
            finally:
                await browser.close()
                
        return opportunities

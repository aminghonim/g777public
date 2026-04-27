from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Depends
from typing import List, Dict, Any
import logging
import os
import json
from datetime import datetime
from pathlib import Path
from core.config import settings

# Logic Imports
from backend.market_intelligence.core import MarketIntelligenceManager
from backend.market_intelligence.sources.maps_extractor import MapsExtractor
from backend.market_intelligence.sources.social_scraper import SocialScraper
from core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Models ---

# --- Endpoints ---


@router.get("/opportunities")
async def get_opportunities(
    limit: int = 20,
    source: str = Query("all", pattern="^(all|maps|social)$"),
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Retrieve aggregated opportunity data from scrapers.
    Reads from local JSON storage for now.
    """
    results = []

    # Updated to use settings and robust path resolution
    root_dir = Path(__file__).resolve().parents[2]
    data_dir = root_dir / settings.system.data_dir

    if not data_dir.exists():
        return {
            "count": 0,
            "results": [],
            "message": f"No data directory found at {data_dir}",
        }

    try:
        # 1. Google Maps Data
        if source in ["all", "maps"]:
            maps_files = [
                f for f in os.listdir(data_dir) if f.startswith("maps_results_")
            ]
            for f in maps_files:
                with open(data_dir / f, "r", encoding="utf-8") as file:
                    try:
                        data = json.load(file)
                        # Enrich with source type
                        if isinstance(data, dict) and "results" in data:
                            for item in data["results"]:
                                item["_source"] = "maps"
                                item["_scraped_at"] = data.get("timestamp")
                            results.extend(data["results"])
                    except json.JSONDecodeError:
                        continue

        # 2. Social Media Data
        if source in ["all", "social"]:
            social_files = [
                f for f in os.listdir(data_dir) if f.startswith("social_results_")
            ]
            for f in social_files:
                with open(data_dir / f, "r", encoding="utf-8") as file:
                    try:
                        data = json.load(file)
                        # Enrich with source type
                        if isinstance(data, dict) and "results" in data:
                            for item in data["results"]:
                                item["_source"] = "social"
                                item["_scraped_at"] = data.get("timestamp")
                            results.extend(data["results"])
                    except json.JSONDecodeError:
                        continue

        # Sort by date (newest first)
        results.sort(key=lambda x: x.get("_scraped_at", 0), reverse=True)

        return {"count": len(results), "limit": limit, "results": results[:limit]}

    except Exception as e:
        logger.error(f"Intelligence fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger_scan")
async def trigger_scan(
    background_tasks: BackgroundTasks,
    type: str = Query(..., pattern="^(maps|social|group)$"),
    keyword: str = Query(...),
    country: str = Query(""),
    scrolling_depth: int = Query(2),
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Manually trigger a scraping job.
    """

    async def _run_scraper():
        try:
            if type == "maps":
                scraper = MapsExtractor(headless=True)
                await scraper.scrape(keyword, limit=20, scrolling_depth=scrolling_depth)
            elif type == "social":
                scraper = SocialScraper()
                await scraper.scrape(keyword, limit=20, scrolling_depth=scrolling_depth)
            elif type == "group":
                from backend.group_finder import GroupFinder

                finder = GroupFinder()
                finder.find_groups(keyword, country=country)
            logger.info(f"Scraping job finished: {type} for {keyword}")
        except Exception as e:
            logger.error(f"Scraping job failed: {e}")

    background_tasks.add_task(_run_scraper)

    return {
        "status": "queued",
        "message": f"Started {type} scan for '{keyword}'",
        "eta": "1-2 minutes",
    }

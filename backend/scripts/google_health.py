import os
import sys
import logging
import asyncio
import httpx
from dotenv import load_dotenv
from google import genai
from googleapiclient.discovery import build

# Load environment variables from the root .env
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# Add project root to sys.path to import from backend
sys.path.append(PROJECT_ROOT)

try:
    from backend.core.logging import setup_logging
    # CNS Mandate: Use centralized logging with auto-rotation
    setup_logging()
except ImportError:
    # Fallback if running outside path
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("GoogleHealth")

# Constants
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash")

async def test_gemini_api() -> bool:
    """Tests the Generative Language API (Gemini)."""
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in environment")
        return False
    
    try:
        # Using the new google-genai SDK 
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=AI_MODEL,
            contents="Respond with 'HEALTHY'"
        )
        if response and response.text:
            logger.info("Generative Language API: SUCCESS")
            return True
        else:
            logger.warning("Generative Language API: Empty response")
            return False
    except Exception as e:
        logger.error(f"Generative Language API: FAILED - {str(e)}")
        return False

async def test_places_api() -> bool:
    """Tests the Places API (New)."""
    if not GEMINI_API_KEY:
        return False
    
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GEMINI_API_KEY,
        "X-Goog-FieldMask": "places.displayName"
    }
    data = {"textQuery": "Google"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data, timeout=10.0)
        
        if response.status_code == 200:
            logger.info("Places API (New): SUCCESS")
            return True
        elif response.status_code == 403:
            logger.error("Places API (New): FAILED - 403 Forbidden (Check API enablement/restrictions)")
            return False
        else:
            logger.error(f"Places API (New): FAILED - Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Places API (New): ERROR - {str(e)}")
        return False

async def test_custom_search_api() -> bool:
    """Tests the Custom Search API initialization."""
    if not GEMINI_API_KEY:
        return False
    
    try:
        service = build("customsearch", "v1", developerKey=GEMINI_API_KEY)
        if service:
            logger.info("Custom Search API: INITIALIZED")
            return True
        return False
    except Exception as e:
        logger.error(f"Custom Search API: FAILED - {str(e)}")
        return False

async def run_audit():
    logger.info("🚀 Starting G777 Google API Health Audit...")
    
    # We are focusing on Gemini and Custom Search now as per user request
    # Places API is being skipped/ignored for this run
    results = [
        await test_gemini_api(),
        await test_custom_search_api()
    ]
    
    api_names = ["Gemini", "CustomSearch"]
    summary = dict(zip(api_names, results))
    
    logger.info("--- Audit Summary ---")
    for api, status in summary.items():
        logger.info(f"{api}: {'PASS' if status else 'FAIL'}")
    
    if all(results):
        logger.info("✨ Critical APIs (Gemini & Search) are healthy.")
    else:
        logger.error("🚨 Health check failed for some APIs.")

if __name__ == "__main__":
    asyncio.run(run_audit())

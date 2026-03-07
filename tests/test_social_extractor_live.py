import sys
import os
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from backend.market_intelligence.sources.social_scraper import SocialScraper
import json


def run_safe_test():
    # Force UTF-8 for Windows terminal
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    print("[INFO] Starting Safe Live Test: Social Media Extractor")
    print("-" * 50)

    scraper = SocialScraper()
    keyword = "Real Estate Cairo"
    limit = 5  # Restricted but enough for a test

    print(f"Searching for: '{keyword}' (Limit: {limit} results)")

    try:
        response = scraper.scrape(keyword, limit=limit)

        if response.get("success"):
            results = response.get("results", [])
            print(f"Success! Found {len(results)} results.")
            for i, res in enumerate(results, 1):
                print(f"\nResult #{i}:")
                print(f"  - Title: {res.get('title', 'N/A')}")
                print(f"  - URL: {res.get('url')}")
                print(f"  - Contacts: {res.get('contacts', 'N/A')}")
        else:
            print(f"Scraper returned an error: {response.get('error')}")

    except Exception as e:
        print(f"Critical Failure: {e}")


if __name__ == "__main__":
    run_safe_test()

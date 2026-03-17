"""
API Helpers Module
Provides utility functions for loading configurations and making API calls.
"""
import os
import yaml
import aiohttp  # pylint: disable=unused-import,import-error

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config",
    "api_config.yaml"
)

def load_api_config():
    """
    Loads the API configuration from the yaml file.
    Returns an empty dict if the file is not found or fails to load.
    """
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception:  # pylint: disable=broad-exception-caught
        return {}

async def smart_shorten(url: str, logger=None) -> str:
    """
    يقوم بتقصير الرابط باستخدام CleanURI مع التبديل التلقائي إلى Spoo.me في حال الفشل
    """
    config = load_api_config().get('apis', {}).get('shortener', {})

    primary_url = config.get("primary", "https://cleanuri.com/api/v1/shorten")
    fallback_url = config.get("fallback", "https://spoo.me/")
    timeout = config.get("timeout_seconds", 5)

    # 1. Try Primary (CleanURI)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(primary_url, data={"url": url}, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("result_url", url)
    except Exception as e:  # pylint: disable=broad-exception-caught
        if logger:
            logger(f"Primary shortener failed: {e}. Trying fallback...", "WARN")

    # 2. Try Fallback (Spoo.me)
    # Spoo.me requires different format: Form data with 'url'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                fallback_url,
                data={"url": url},
                headers={"Accept": "application/json"},
                timeout=timeout
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    return data.get("short_url", url)
    except Exception as e:  # pylint: disable=broad-exception-caught
        if logger:
            logger(f"Fallback shortener also failed: {e}. Using original URL.", "ERROR")

    return url

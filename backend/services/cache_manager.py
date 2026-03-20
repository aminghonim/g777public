import os
from upstash_redis import Redis
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed

class CacheManager:
    """
    Modular client to handle standard Redis operations via Upstash Serverless REST API.
    Used for caching and rate-limiting to protect API budgets (Rule 11).
    """

    def __init__(self):
        url = os.getenv("UPSTASH_REDIS_REST_URL")
        token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        
        self.client = None
        if url and token:
            try:
                self.client = Redis(url=url, token=token)
            except Exception as e:
                logger.error(f"Failed to initialize Upstash Redis: {str(e)}")
        else:
            logger.warning("Upstash credentials not found. Caching disabled.")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def set(self, key: str, value: str, ex: int = None):
        """Set a value in cache, optionally with expiration in seconds"""
        if not self.client:
            return False
            
        try:
            self.client.set(key, value, ex=ex)
            return True
        except Exception as e:
            logger.error(f"Redis Set Error: {str(e)}")
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def get(self, key: str):
        """Retrieve a value from cache"""
        if not self.client:
            return None
            
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis Get Error: {str(e)}")
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def check_rate_limit(self, identifier: str, limit: int, window_seconds: int = 60) -> bool:
        """
        Simple rate limiting algorithm. Returns True if allowed, False if blocked.
        Adheres to Rule 11 (Resource Budget Protection).
        """
        if not self.client:
            return True # Fail open if cache is down
            
        key = f"rate_limit:{identifier}"
        try:
            current = self.client.incr(key)
            if current == 1:
                self.client.expire(key, window_seconds)
            
            return current <= limit
        except Exception as e:
            logger.error(f"Rate Limiter Error: {str(e)}")
            return True # Fail open

# Singleton instance
cache_manager = CacheManager()

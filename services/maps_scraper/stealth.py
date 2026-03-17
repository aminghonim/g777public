import random
from typing import List, Dict
import yaml
import os
import logging

class StealthManager:
    """
    Manages stealth strategies including User-Agent rotation and header randomization.
    Follows the Config-First approach by loading settings from YAML.
    """
    
    def __init__(self, config_path: str = "config/maps_scraper.yaml"):
        """
        Initializes the stealth manager by loading configuration.
        
        Args:
            config_path: Path to the YAML configuration file.
        """
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            logging.error(f"Configuration file not found at {config_path}")
            self.config = {}

        self.user_agents: List[str] = self.config.get('stealth', {}).get('user_agents', [])

    def get_random_user_agent(self) -> str:
        """
        Returns a random User-Agent from the configured list.
        
        Returns:
            A User-Agent string.
        """
        if not self.user_agents:
            # CNS Rule: Defensive coding with sensible fallbacks
            return ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        return random.choice(self.user_agents)

    def get_stealth_headers(self) -> Dict[str, str]:
        """
        Returns a dictionary of headers to aid in detection avoidance.
        
        Returns:
            Dictionay of HTTP headers.
        """
        return {
            "User-Agent": self.get_random_user_agent(),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }

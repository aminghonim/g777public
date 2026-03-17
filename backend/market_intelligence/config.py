import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class NicheConfigModel(BaseModel):
    niche: str = "general"
    location: str = "Egypt"
    keywords: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    sources: Dict[str, bool] = Field(default_factory=lambda: {
        "google_trends": True,
        "tiktok": False,
        "meta_ads": False,
        "google_maps": True
    })
    weights: Dict[str, float] = Field(default_factory=lambda: {
        "frequency": 0.4,
        "growth": 0.3,
        "relevance": 0.3
    })

class ConfigLoader:
    def __init__(self, config_path: str = "config/niche_config.yaml"):
        self.config_path = Path(config_path)
        self._config: Optional[NicheConfigModel] = None

    def load(self) -> NicheConfigModel:
        """Loads and validates the niche configuration."""
        if not self.config_path.exists():
            # Return default if file doesn't exist
            return NicheConfigModel()
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self._config = NicheConfigModel(**data)
        except Exception as e:
            print(f"[MarketIntelligence] Error loading config: {e}")
            # Fallback to default
            self._config = NicheConfigModel()
            
        return self._config

    @property
    def config(self) -> NicheConfigModel:
        if self._config is None:
            self.load()
        return self._config

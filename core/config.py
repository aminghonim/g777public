from pydantic import BaseModel, Field, ConfigDict
from pydantic_settings import BaseSettings
import yaml
import os
from typing import Optional, List, Dict, Any


class SystemConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    app_name: str = "Antigravity G777"
    version: str = "2.2.0"
    environment: str = "production"
    log_level: str = "INFO"
    data_dir: str = "data"
    exempt_paths: List[str] = [
        "/health",
        "/docs",
        "/openapi.json",
        "/auth/login",
        "/auth/register",
        "/auth/config",
        "/auth/guest-login",
        "/auth/license/activate",
        "/auth/license/guest",
        "/webhook/whatsapp",
        "/webhook/health",
        "/api/webhook/evolution",
        "/monitoring/sentry-webhook",
        # REMOVED: /auth/license/generate — admin-only, must be authenticated
        # REMOVED: /system/update/apply — admin-only, must be authenticated
        # REMOVED: /system/stream/events — SSE, can use handshake token
    ]


class SecurityConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    token_header: str = "X-G777-Auth-Token"
    session_file: str = "secure_session.json"
    temp_dir: str = ".antigravity"
    max_retries: int = 3
    max_msg_per_hour: int = 200
    auth_required: bool = True
    allow_guest_access: bool = True
    # No default — must be set via env or config
    guest_secret: str = ""
    guest_username: str = "guest_admin"
    guest_instance_name: str = "G777_Guest"
    guest_email: str = "guest@localhost"
    # SAAS-018: Paths exempt from license expiry checks (auth + public routes)
    license_exempt_paths: List[str] = [
        "/health",
        "/docs",
        "/openapi.json",
        "/auth/login",
        "/auth/register",
        "/auth/config",
        "/auth/guest-login",
        "/auth/license/activate",
        "/auth/license/guest",
        "/auth/license/status",
        "/webhook/whatsapp",
        "/webhook/health",
        "/api/webhook/evolution",
    ]


class EvolutionApiConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    url: str = ""
    api_key: str = ""
    instance_name: str = ""
    baileys_api_url: Optional[str] = None


class DelayConfigValues(BaseModel):
    model_config = ConfigDict(extra="ignore")
    min: int
    max: int


class DelayConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    campaign: DelayConfigValues
    scraping: DelayConfigValues


class WorkingHoursConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    start: int = 9
    end: int = 22


class FeaturesConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    google_maps: Dict[str, Any] = {}
    whatsapp_warmer: Dict[str, Any] = {}


class NetworkConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    host: str = "127.0.0.1"
    default_port: int = 0
    # No wildcard — must be explicitly configured via env or config.yaml
    cors_origins: list[str] = []


class UpdateConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    check_url: str = ""
    download_base_url: str = ""
    channel: str = "stable"
    enable_auto_check: bool = True
    bootstrapper_path: str = "scripts/updater_bootstrapper.py"


class Config(BaseSettings):
    model_config = ConfigDict(extra="ignore")
    system: SystemConfig = SystemConfig()
    security: SecurityConfig = SecurityConfig()
    network: NetworkConfig = NetworkConfig()
    evolution_api: Optional[EvolutionApiConfig] = None
    delays: Optional[DelayConfig] = None
    working_hours: Optional[WorkingHoursConfig] = None
    features: Optional[FeaturesConfig] = None
    updates: UpdateConfig = UpdateConfig()

    @classmethod
    def load_from_yaml(cls, path: str = "config.yaml"):
        if not os.path.exists(path):
            return cls()
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return cls(**data) if data else cls()


# Singleton instance
settings = Config.load_from_yaml()

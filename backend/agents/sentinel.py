import logging
import time
import os
import yaml
import sqlite3
import psutil
from typing import Dict, Any

logger = logging.getLogger("SentinelAgent")


class SentinelAgent:
    def __init__(self, orchestrator, config_path: str = "config/sentinel_rules.yaml"):
        self.orchestrator = orchestrator
        self.name = "Sentinel"
        self.config = self._load_config(config_path)
        self.db_path = self.config.get("logging", {}).get(
            "db_path", "data/sentinel_metrics.db"
        )
        self._init_db()

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load anomaly detection rules."""
        if not os.path.exists(path):
            logger.warning(f"Config {path} not found. Using defaults.")
            return {}
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load Sentinel config: {e}")
            return {}

    def _init_db(self):
        """Initialize lightweight metrics DB."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                metric_type TEXT,
                value REAL,
                details TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    def log_metric(self, metric_type: str, value: float, details: str = ""):
        """Log a system metric to the DB."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO metrics (timestamp, metric_type, value, details) VALUES (?, ?, ?, ?)",
                (time.time(), metric_type, value, details),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log metric: {e}")

    def check_health(self):
        """Main monitoring loop (can be called periodically or per-request)."""
        # 1. Check Latency (Simulated via recent logs or active monitoring)
        pass  # Latency is checked per-request in Orchestrator

        # 2. Check Memory
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.log_metric("memory_usage_mb", memory_mb)

        limit_mb = self.config.get("thresholds", {}).get("memory_limit_mb", 500)
        if memory_mb > limit_mb:
            self._trigger_anomaly(
                "High Memory Usage", f"{memory_mb:.2f} MB > {limit_mb} MB"
            )

    def analyze_request(self, latency_ms: float):
        """Called by Orchestrator after each request."""
        self.log_metric("request_latency_ms", latency_ms)

        limit_ms = self.config.get("thresholds", {}).get("latency_max_ms", 15000)
        if latency_ms > limit_ms:
            self._trigger_anomaly(
                "High Latency", f"{latency_ms:.2f} ms > {limit_ms} ms"
            )

    def _trigger_anomaly(self, anomaly_type: str, details: str):
        """Handle detected anomaly."""
        logger.warning(f"[SENTINEL ALERT] {anomaly_type} - {details}")
        # Here we could trigger self-healing actions (e.g., GC, restarts)
        # For now, we just log and potentially advise the Orchestrator.

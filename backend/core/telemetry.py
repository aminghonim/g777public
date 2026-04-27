import asyncio
import psutil
import logging
from backend.core.event_broker import event_broker

logger = logging.getLogger("g777.telemetry")


async def start_telemetry_monitoring(interval_seconds: int = 10):
    """
    Background worker that monitors CPU and RAM usage and publishes to the event broker.
    Unified SSE Pipeline (Gap 2 Compliance).
    """
    logger.info(f"Starting Telemetry Monitoring (Interval: {interval_seconds}s)")
    while True:
        try:
            # interval=0.1 means psutil will wait for 0.1s to calculate % diff
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent

            await event_broker.publish_telemetry(cpu=cpu, ram=ram)
        except Exception as e:
            logger.error(f"Telemetry error: {e}")

        await asyncio.sleep(interval_seconds)

import psutil
import logging
import time
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SystemVitality:
    cpu_percent: float
    memory_percent: float
    net_sent: int
    net_recv: int


class SystemMonitor:
    """
    Monitors system resources (CPU, RAM, Network) using psutil.
    """

    def __init__(self, cpu_threshold: float = 80.0, memory_threshold: float = 85.0):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold

    def get_vitality(self) -> SystemVitality:
        """Returns current system vitality stats."""
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        net = psutil.net_io_counters()

        return SystemVitality(
            cpu_percent=cpu,
            memory_percent=memory,
            net_sent=net.bytes_sent,
            net_recv=net.bytes_recv,
        )

    def check_health(self):
        """Checks if system vitals are within safe thresholds."""
        vitals = self.get_vitality()

        if vitals.cpu_percent > self.cpu_threshold:
            logger.warning(f"High CPU Usage: {vitals.cpu_percent}%")
            # Potential self-healing trigger here

        if vitals.memory_percent > self.memory_threshold:
            logger.warning(f"High Memory Usage: {vitals.memory_percent}%")
            # Potential self-healing trigger here

        return vitals

    def kill_process_by_name(self, process_name: str) -> bool:
        """Attempts to kill a process by its name (Self-Healing)."""
        killed = False
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if process_name.lower() in proc.info["name"].lower():
                    proc.kill()
                    logger.info(
                        f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})"
                    )
                    killed = True
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ) as e:
                logger.error(f"Failed to kill process {process_name}: {e}")
        return killed


if __name__ == "__main__":
    # Test execution
    monitor = SystemMonitor()
    print("Monitoring System Vitality (Press Ctrl+C to stop)...")
    try:
        while True:
            vitals = monitor.check_health()
            print(
                f"CPU: {vitals.cpu_percent}% | RAM: {vitals.memory_percent}% | Net Sent: {vitals.net_sent} | Net Recv: {vitals.net_recv}"
            )
            time.sleep(2)
    except KeyboardInterrupt:
        print("Monitoring stopped.")

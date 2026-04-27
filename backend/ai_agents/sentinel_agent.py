from google import adk
import logging
import os
import psutil

logger = logging.getLogger("ADKSentinel")


class SentinelAgent(adk.Agent):
    """
    ADK-compliant Sentinel Agent.
    Specializes in system monitoring, health checks, and anomaly detection.
    """

    def __init__(self):
        super().__init__(
            name="Platform-Guardian",
            instructions="""
            ROLE: System Reliability Engineer (SRE).
            TASK: Monitor system vitals, detect anomalies, and ensure high availability.
            
            GUIDELINES:
            1. Monitor CPU, RAM, and Latency.
            2. Log all anomalies to the system metrics database.
            3. Proactively alert the Orchestrator regarding performance degradation.
            4. Use 'check_system_status' and 'get_recent_logs' tools.
            """,
        )

    def get_system_vitals(self):
        """Fetch current system usage."""
        return {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage("/").percent,
        }

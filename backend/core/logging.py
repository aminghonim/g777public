import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_file="g777.log", level=logging.INFO):
    """
    Sets up global logging with rotation.
    CNS Mandate: Auto-Log Rotation to prevent file bloat.
    """
    # Get the project root directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    log_path = os.path.join(root_dir, log_file)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if setup is called multiple times
    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
        # 10MB max per file, 5 backup files
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # Also log to console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        logging.info(f"Log rotation initialized: {log_path} (10MB max, 5 backups)")

# Singleton logger for the module
logger = logging.getLogger("g777_core")

# Self-initialize on import if not already set up
setup_logging()

import socket
import logging
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def validate_webhook_reachability():
    """
    Verify all configured webhook targets are DNS-resolvable.
    This runs on startup to fail fast if configuration is broken.
    """
    logger.info("🛡️ STARTUP CHECK: Validating Webhook Reachability...")
    
    # List of critical URLs to check
    targets = {
        'EVOLUTION_API': os.getenv('EVOLUTION_API_URL'),
        'N8N_WEBHOOK': os.getenv('N8N_WEBHOOK_URL'),
        'BAILEYS_API': os.getenv('BAILEYS_API_URL')
    }
    
    failures = []
    
    for name, url in targets.items():
        if not url:
            logger.info(f"ℹ️ {name}: Not configured (Skipping)")
            continue
            
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            
            # Skip check for localhost/IPs to avoid redundancy, focusing on DNS
            if not hostname:
                 failures.append(f"{name} (Invalid URL: {url})")
                 continue
                 
            # Resolve DNS
            ip_address = socket.gethostbyname(hostname)
            logger.info(f"✅ {name}: {hostname} -> {ip_address}")
            
        except socket.gaierror:
            # If on Windows/Local and hostname looks like a Docker service (no dots), it's expected to fail outside Docker.
            if os.name == 'nt' and '.' not in hostname:
                logger.warning(f"⚠️ {name}: {hostname} could not be resolved (Expected if running locally outside Docker)")
            else:
                logger.error(f"❌ {name}: {hostname} CANNOT BE RESOLVED!")
                failures.append(f"{name} ({hostname})")
        except Exception as e:
            logger.warning(f"⚠️ {name}: DNS check warning: {e}")
    
    if failures:
        error_msg = f"Startup Failed: DNS Resolution Error for {', '.join(failures)}"
        logger.critical(error_msg)
        print(f"\n[FATAL] {error_msg}\n")
    else:
        logger.info("🚀 All Network Dependencies Resolved Successfully.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    validate_webhook_reachability()

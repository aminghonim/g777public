import os
import yaml
import re
from urllib.parse import urlparse
from dotenv import dotenv_values


def validate_config():
    print("Starting Configuration Validation...")
    
    # 1. Load .env
    env_vars = dotenv_values(".env")
    print(f"Loaded .env ({len(env_vars)} variables)")

    # 2. Extract Hostnames from .env URLs
    # Looking for variables ending in _URL or specific known keys
    urls_to_check = {}
    for key, value in env_vars.items():
        if "_URL" in key or key in ["WEBHOOK_URL", "N8N_WEBHOOK_URL"]:
            if value and value.startswith("http"):
                try:
                    parsed = urlparse(value)
                    hostname = parsed.hostname

                    # Filter out external IPs/domains (very basic check)
                    if (hostname not in ["localhost", "127.0.0.1", "0.0.0.0"] 
                        and not re.match(r"^\d{1,3}\.", hostname)
                        and "supabase.co" not in hostname
                        and "googleapis.com" not in hostname):
                         urls_to_check[key] = hostname
                except:
                    pass

    print(f"Found {len(urls_to_check)} internal hostnames to validate:")
    for k, v in urls_to_check.items():
        print(f"   - {k}: {v}")

    # 3. Load docker-compose.yaml
    try:
        with open("docker-compose.yaml", "r") as f:
            compose = yaml.safe_load(f)
    except FileNotFoundError:
        print("docker-compose.yaml not found!")
        return False

    services = compose.get('services', {})
    print(f"Found {len(services)} Docker services")

    # 4. Build List of Valid Internal DNS Names
    valid_hosts = []
    
    for service_name, config in services.items():
        # Service Name is always a valid hostname
        valid_hosts.append(service_name)
        
        # Container Name (Logic: Docker creates DNS for container_name ONLY if on custom network, 
        # but standard practice is Service Name. We'll be strict and warn if only container_name matches)
        # Actually in recent Docker Compose, Service Name is the reliable DNS.
        container_name = config.get('container_name')
        if container_name:
             valid_hosts.append(container_name) 
        
        # Networks Aliases
        networks = config.get('networks', {})
        if isinstance(networks, dict):
            for net_name, net_config in networks.items():
                if isinstance(net_config, dict):
                    aliases = net_config.get('aliases', [])
                    if aliases:
                        valid_hosts.extend(aliases)
        elif isinstance(networks, list):
             # Simple list format doesn't support aliases
             pass

    print(f"Valid Docker Hostnames: {valid_hosts}")

    # 5. Cross-Reference
    errors = []
    for key, hostname in urls_to_check.items():
        if hostname not in valid_hosts:
            errors.append(f"ERROR: {key} points to '{hostname}', but no service/alias exists with this name!")
        else:
            print(f"OK: {key} -> {hostname} (Verified)")

    print("-" * 30)
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(e)
        return False
    else:
        print("ALL SYSTEMS GO! Configuration is consistent.")
        return True

if __name__ == "__main__":
    if not validate_config():
        exit(1)

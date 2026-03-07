import os
import yaml
import re
import argparse
import shutil
from datetime import datetime
from dotenv import dotenv_values, set_key

# Configuration
DOCKER_COMPOSE_FILE = 'docker-compose.yaml'
ENV_FILE = '.env'

def load_docker_services():
    """Extract service names from docker-compose.yaml"""
    if not os.path.exists(DOCKER_COMPOSE_FILE):
        print(f"❌ Error: {DOCKER_COMPOSE_FILE} not found!")
        return {}
    
    with open(DOCKER_COMPOSE_FILE, 'r') as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML: {e}")
            return {}
            
    services = {}
    if 'services' in data:
        for service_name, config in data['services'].items():
            # We use the key (service name) as the primary DNS hostname in Docker network
            # container_name is also valid but service name is preferred for internal networking
            services[service_name] = {
                'container_name': config.get('container_name'),
                'ports': config.get('ports', [])
            }
    return services

def audit_env_file(services, fix=False):
    """Check .env URLs against Docker services"""
    if not os.path.exists(ENV_FILE):
        print(f"❌ Error: {ENV_FILE} not found!")
        return

    print(f"🔍 Auditing {ENV_FILE} against {len(services)} Docker services...")
    
    env_vars = dotenv_values(ENV_FILE)
    
    # Common misconfigurations to look for
    # (Mapping: Incorrect Name -> Correct Service Name)
    # We infer this by looking at what's in services
    
    known_aliases = {
        'g777-brain': 'g777-backend',
        'n8n-engine': 'n8n',
        'baileys': 'baileys-service',
        'evolution': 'evolution-api'
    }
    
    changes = []
    
    for key, value in env_vars.items():
        if not value or not isinstance(value, str):
            continue
            
        # Extract hostname from URL (simple regex)
        match = re.search(r'http://([^:/]+)(?::(\d+))?', value)
        if match:
            hostname = match.group(1)
            port = match.group(2)
            
            # Skip IPs and localhost
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', hostname) or hostname == 'localhost':
                continue
                
            # Check if hostname matches a known service
            if hostname in services:
                print(f"✅ {key}: {hostname} (Valid Service)")
            elif hostname in known_aliases:
                correct_service = known_aliases[hostname]
                if correct_service in services:
                    print(f"❌ {key}: Found '{hostname}', should be '{correct_service}'")
                    changes.append((key, hostname, correct_service))
                else:
                    print(f"⚠️ {key}: Alias '{hostname}' maps to '{correct_service}' but service not found in compose!")
            else:
                 # Check if it matches a container_name but not service name
                 found = False
                 for svc_name, cfg in services.items():
                     if cfg['container_name'] == hostname:
                         print(f"⚠️ {key}: Uses container_name '{hostname}'. Recommendation: Use service name '{svc_name}'")
                         # changes.append((key, hostname, svc_name)) # Optional: Enforce service name
                         found = True
                         break
                 if not found:
                     print(f"❓ {key}: Hostname '{hostname}' not found in Docker services.")

    if changes:
        print("\n📋 Proposed Changes:")
        for key, old, new in changes:
            print(f"  - {key}: {old} -> {new}")
            
        if fix:
            backup_file = f"{ENV_FILE}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy(ENV_FILE, backup_file)
            print(f"\n💾 Backup created: {backup_file}")
            
            for key, old, new in changes:
                # We need to preserve the rest of the URL
                current_val = env_vars[key]
                new_val = current_val.replace(old, new)
                set_key(ENV_FILE, key, new_val)
                print(f"  ✅ Fixed {key}")
            print("\n✨ All fixes applied!")
        else:
            print("\n💡 Run with --auto to apply these fixes.")
    else:
        print("\n✅ No critical DNS mismatches found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit and Fix Docker DNS in .env")
    parser.add_argument("--auto", action="store_true", help="Automatically apply fixes")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change")
    
    args = parser.parse_args()
    
    docker_services = load_docker_services()
    if docker_services:
        audit_env_file(docker_services, fix=args.auto)

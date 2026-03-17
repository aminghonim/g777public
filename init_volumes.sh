#!/bin/bash
# G777 Docker Volume Initializer
# Run ONCE before first 'docker compose up' to prevent root-owned directories.
# Usage: bash init_volumes.sh

set -e

DIRS=("auth_info" "data/evolution_db" "data/evolution_instances")

for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "[OK] Created: $dir"
    else
        echo "[SKIP] Already exists: $dir"
    fi
done

# Ensure current user owns everything (prevents root lock-out in Docker)
chown -R "$(id -u):$(id -g)" auth_info/ data/

echo ""
echo "[DONE] All volumes initialized with UID=$(id -u), GID=$(id -g)."
echo "You can now run: docker compose --profile full up --build"

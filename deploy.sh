#!/bin/bash
# ─────────────────────────────────────────────────────────────
# deploy.sh — Run this on the DigitalOcean Droplet to deploy
# or re-deploy (pull latest code + rebuild + restart)
# ─────────────────────────────────────────────────────────────
set -e

echo "🚀 Starting deployment..."

# 1. Pull latest code
git pull origin main

# 2. Rebuild and restart containers (zero-downtime order: db → backend → frontend)
docker-compose -f docker-compose.prod.yml up -d --build --remove-orphans

# 3. Wait for backend to be ready
echo "⏳ Waiting for backend to be healthy..."
sleep 8

# 4. Run enum migration (safe to run every time — idempotent)
docker-compose -f docker-compose.prod.yml exec -T backend python migrate_roles.py

# 5. Run seed (skips existing records automatically)
docker-compose -f docker-compose.prod.yml exec -T backend python seed.py

# 6. Clean up old Docker images
docker image prune -f

echo "✅ Deployment complete!"
echo "   App is running at http://$(curl -s ifconfig.me)"

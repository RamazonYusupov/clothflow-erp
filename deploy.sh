#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy.sh — Deploy / redeploy on the DigitalOcean Droplet
# Prerequisites: ./init-ssl.sh must have been run once first
# ─────────────────────────────────────────────────────────────────────────────
set -e

echo "🚀 Starting deployment..."

# 1. Pull latest code from GitHub
git pull origin main

# 2. Rebuild and restart all containers
docker compose -f docker-compose.prod.yml up -d --build --remove-orphans

# 3. Wait for backend to be healthy
echo "⏳ Waiting for backend to start..."
sleep 10

# 4. Run enum migration (idempotent — safe to run every time)
docker compose -f docker-compose.prod.yml exec -T backend python migrate_roles.py

# 5. Seed database (skips records that already exist)
docker compose -f docker-compose.prod.yml exec -T backend python seed.py

# 6. Remove dangling images to free disk space
docker image prune -f

echo ""
echo "✅ Deployment complete!"
echo "   🌐  https://clothflow.systems"
echo "   🌐  https://www.clothflow.systems"
echo "   📖  https://clothflow.systems/api/docs"

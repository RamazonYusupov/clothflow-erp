#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# init-ssl.sh
# Run this ONCE on the server before the first deploy to get SSL certificates.
# After this, deploy.sh handles everything including auto-renewal.
# ─────────────────────────────────────────────────────────────────────────────
set -e

DOMAIN="clothflow.systems"
EMAIL="ramzan06@gmail.com"   # ← Let's Encrypt expiry notifications go here

echo "🔐 Obtaining SSL certificate for $DOMAIN and www.$DOMAIN ..."

# 1. Make sure port 80 is free (stop frontend if already running)
docker compose -f docker-compose.prod.yml stop frontend 2>/dev/null || true

# 2. Install certbot on the host (only needed once)
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing certbot..."
    apt update -qq
    apt install -y certbot
fi

# 3. Get the certificate using standalone mode (temporary HTTP server on port 80)
certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo "✅ Certificate obtained!"
echo "   Location: /etc/letsencrypt/live/$DOMAIN/"
echo ""
echo "Now run: ./deploy.sh"

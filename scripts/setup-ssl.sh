#!/bin/bash

# SSL Setup Script for Coventure.es URL Shortener
# Usage: ./setup-ssl.sh coventure.es

set -e

DOMAIN=${1:-coventure.es}
EMAIL=${2:-"admin@${DOMAIN}"}

echo "🔒 Setting up SSL certificates for ${DOMAIN}..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root for security reasons"
   exit 1
fi

# Install certbot if not present
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# Stop nginx if running to free port 80
echo "⏹️  Stopping nginx temporarily..."
sudo systemctl stop nginx 2>/dev/null || true
docker-compose -f docker-compose.prod.yml stop nginx 2>/dev/null || true

# Generate certificates
echo "🔐 Generating SSL certificates for ${DOMAIN}..."
sudo certbot certonly \
    --standalone \
    --email "${EMAIL}" \
    --agree-tos \
    --non-interactive \
    --domains "${DOMAIN},www.${DOMAIN}"

# Create ssl directory if it doesn't exist
mkdir -p ssl

# Copy certificates to project directory
echo "📋 Copying certificates to project directory..."
sudo cp "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" "./ssl/${DOMAIN}.crt"
sudo cp "/etc/letsencrypt/live/${DOMAIN}/privkey.pem" "./ssl/${DOMAIN}.key"
sudo chown $USER:$USER ./ssl/*
chmod 600 ./ssl/${DOMAIN}.key
chmod 644 ./ssl/${DOMAIN}.crt

# Verify certificates
echo "✅ Verifying certificates..."
openssl x509 -in "./ssl/${DOMAIN}.crt" -text -noout | grep -E "(Subject|Issuer|Not Before|Not After)"

# Set up auto-renewal cron job
echo "🔄 Setting up auto-renewal..."
(crontab -l 2>/dev/null | grep -v certbot; echo "0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'docker-compose -f /path/to/docker-compose.prod.yml restart nginx'") | crontab -

echo "✨ SSL setup complete!"
echo "📁 Certificates installed at:"
echo "   - Certificate: ./ssl/${DOMAIN}.crt"
echo "   - Private Key: ./ssl/${DOMAIN}.key"
echo ""
echo "🚀 You can now start the production deployment:"
echo "   docker-compose -f docker-compose.prod.yml up -d"
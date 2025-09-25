#!/bin/bash
# Domain Configuration Script for URL Shortener
# Usage: ./scripts/setup-domain.sh your-domain.com

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <domain>"
    echo "Example: $0 example.com"
    exit 1
fi

DOMAIN=$1
PROJECT_DIR=$(dirname "$(dirname "$0")")

echo "🌐 Setting up URL Shortener for domain: $DOMAIN"

# Update backend .env file
if [ -f "$PROJECT_DIR/.env" ]; then
    echo "📝 Updating existing .env file..."
    sed -i "s/^DOMAIN=.*/DOMAIN=$DOMAIN/" "$PROJECT_DIR/.env"
    sed -i "s|^BASE_URL=.*|BASE_URL=https://$DOMAIN|" "$PROJECT_DIR/.env"
    sed -i "s|ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN|" "$PROJECT_DIR/.env"
else
    echo "📝 Creating .env file from template..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    sed -i "s/coventure\.es/$DOMAIN/g" "$PROJECT_DIR/.env"
fi

# Update frontend .env.production
if [ -f "$PROJECT_DIR/frontend/.env.production" ]; then
    echo "📝 Updating frontend production config..."
    sed -i "s|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=https://$DOMAIN|" "$PROJECT_DIR/frontend/.env.production"
else
    echo "📝 Creating frontend production config..."
    cp "$PROJECT_DIR/frontend/.env.production.example" "$PROJECT_DIR/frontend/.env.production"
    sed -i "s|https://your-domain\.com|https://$DOMAIN|" "$PROJECT_DIR/frontend/.env.production"
fi

# Update nginx configuration
if [ -f "$PROJECT_DIR/nginx.conf" ]; then
    echo "📝 Updating nginx configuration..."
    sed -i "s/server_name .*/server_name $DOMAIN www.$DOMAIN;/" "$PROJECT_DIR/nginx.conf"
    sed -i "s|ssl_certificate .*crt;|ssl_certificate /etc/ssl/certs/$DOMAIN.crt;|" "$PROJECT_DIR/nginx.conf"
    sed -i "s|ssl_certificate_key .*key;|ssl_certificate_key /etc/ssl/private/$DOMAIN.key;|" "$PROJECT_DIR/nginx.conf"
fi

echo "✅ Domain configuration complete!"
echo ""
echo "Next steps:"
echo "1. Update DNS records to point $DOMAIN to your server"
echo "2. Set up SSL certificates for $DOMAIN"
echo "3. Update docker-compose.prod.yml environment variables"
echo "4. Deploy with: DOMAIN=$DOMAIN docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "DNS Records needed:"
echo "A     $DOMAIN         → YOUR_SERVER_IP"
echo "A     www.$DOMAIN     → YOUR_SERVER_IP"
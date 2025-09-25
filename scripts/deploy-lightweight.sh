#!/bin/bash
# Lightweight Deployment Script for URL Shortener
# Usage: ./scripts/deploy-lightweight.sh your-domain.com

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <domain>"
    echo "Example: $0 example.com"
    exit 1
fi

DOMAIN=$1
PROJECT_DIR=$(dirname "$(dirname "$0")")

echo "🪶 Setting up lightweight deployment for: $DOMAIN"

# 1. Configure domain
echo "📝 Configuring domain..."
"$PROJECT_DIR/scripts/setup-domain.sh" "$DOMAIN"

# 2. Set up backend
echo "🐍 Setting up Python backend..."
cd "$PROJECT_DIR/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt  # SQLite-based dependencies

# 3. Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/url-shortener.service << EOF
[Unit]
Description=URL Shortener ($DOMAIN)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
Environment=DOMAIN=$DOMAIN
Environment=ENVIRONMENT=production
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 4. Set up nginx
echo "🌐 Configuring nginx..."
sudo apt update -qq
sudo apt install -y nginx

sudo tee /etc/nginx/sites-available/url-shortener << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Health check endpoint
    location /api/health {
        proxy_pass http://127.0.0.1:8000/api/health;
        access_log off;
    }
}
EOF

# Enable the site
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/url-shortener /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 5. Start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable url-shortener
sudo systemctl start url-shortener

# 6. Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 5

# 7. Test deployment
echo "🧪 Testing deployment..."
if curl -s "http://localhost:8000/api/health" > /dev/null; then
    echo "✅ Backend service is running"
else
    echo "❌ Backend service failed to start"
    sudo systemctl status url-shortener --no-pager -l
    exit 1
fi

if curl -s "http://$DOMAIN/api/health" > /dev/null; then
    echo "✅ Nginx proxy is working"
else
    echo "❌ Nginx proxy configuration failed"
    sudo nginx -t
    exit 1
fi

echo ""
echo "🎉 Lightweight deployment complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Set up SSL: sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo "2. Test your URL shortener: http://$DOMAIN"
echo "3. Monitor logs: sudo journalctl -u url-shortener -f"
echo ""
echo "📊 Service Management:"
echo "• Status:  sudo systemctl status url-shortener"
echo "• Restart: sudo systemctl restart url-shortener"
echo "• Logs:    sudo journalctl -u url-shortener -f"
echo ""
echo "💰 Monthly cost: ~$3-5 (512MB VPS)"
echo "📈 Capacity: ~100 URLs/day, perfect for personal use"
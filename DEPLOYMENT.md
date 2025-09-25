# 🚀 URL Changer - Production Deployment Guide

> **Note**: Throughout this guide, replace `YOUR_DOMAIN` with your actual domain name (e.g., `example.com`).
> 
> **Quick Setup**: Use `./scripts/setup-domain.sh your-domain.com` to automatically configure all files for your domain.

## 🔑 NEW: API Key Authentication (UPDATED)

### **Frontend Authentication Integration**
✅ **Frontend now automatically handles API key authentication!**

- **Development**: No API key required
- **Production**: API key automatically included in all requests
- **Seamless**: No manual header management needed

### **Environment Configuration**

**Frontend (`.env.production`)**:
```bash
VITE_API_BASE_URL=https://YOUR_DOMAIN
VITE_API_KEY=JCffTVvDzYiOUqTFrJmTNAMa9ql6kcvC
```

**Backend (`.env.production`)**:  
```bash
ENVIRONMENT=production
API_KEY=JCffTVvDzYiOUqTFrJmTNAMa9ql6kcvC
SECRET_KEY=arNgJAJLTp1h%zWP2LRe#FqtGyhpotlpMbsl%YL0tuZtu0V8K2Badh%76Fwovvc2
```

### **Test Authentication**
```bash
./test-api-auth.sh  # Verify API key setup
```

## Prerequisites

### 1. Domain & DNS Configuration
```bash
# DNS Records for your domain (replace YOUR_DOMAIN with your actual domain)
A     YOUR_DOMAIN         → YOUR_SERVER_IP
A     www.YOUR_DOMAIN     → YOUR_SERVER_IP
CNAME api.YOUR_DOMAIN     → YOUR_DOMAIN
```

### 2. SSL Certificate Setup
```bash
# Using Let's Encrypt (recommended)
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Generate SSL certificates (replace YOUR_DOMAIN with your actual domain)
sudo certbot certonly --standalone -d YOUR_DOMAIN -d www.YOUR_DOMAIN

# Certificates will be generated at:
# /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem
# /etc/letsencrypt/live/YOUR_DOMAIN/privkey.pem

# Copy certificates to project directory
sudo cp /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem ./ssl/YOUR_DOMAIN.crt
sudo cp /etc/letsencrypt/live/YOUR_DOMAIN/privkey.pem ./ssl/YOUR_DOMAIN.key
sudo chown $USER:$USER ./ssl/*
```

### 3. Server Requirements

#### 💰 **Budget-Friendly Options (< $5/month)**
- **VPS**: 512MB RAM, 1 CPU, 10GB storage
- **Examples**: DigitalOcean Basic Droplet ($4/mo), Linode Nanode ($5/mo)
- **Deployment**: SQLite + single container (no PostgreSQL)

#### 🏢 **Standard Production (< $20/month)**  
- **VPS**: 1-2GB RAM, 1-2 CPU, 25GB storage
- **Examples**: Most $10-15/month VPS offerings
- **Deployment**: Full stack with PostgreSQL

#### 🔥 **High Performance ($20+/month)**
- **VPS**: 4GB+ RAM, 2+ CPU, 50GB+ storage
- **For**: Heavy traffic (10,000+ URLs/day)

## Deployment Options

### 🪶 **Option 1: Lightweight Deployment (512MB RAM)**

Perfect for personal use or small projects:

```bash
# 1. Set up domain
./scripts/setup-domain.sh YOUR_DOMAIN

# 2. Install backend only (no Docker needed)
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt  # Uses SQLite instead of PostgreSQL

# 3. Run with systemd (auto-restart)
sudo tee /etc/systemd/system/url-shortener.service << EOF
[Unit]
Description=URL Shortener
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable url-shortener
sudo systemctl start url-shortener

# 4. Set up reverse proxy with nginx (lightweight config)
sudo apt install nginx
sudo tee /etc/nginx/sites-available/url-shortener << EOF
server {
    listen 80;
    server_name YOUR_DOMAIN www.YOUR_DOMAIN;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/url-shortener /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

**Benefits**: Minimal resource usage, simple maintenance, costs under $5/month

---

### 🐳 **Option 2: Full Production Deployment**

For serious production use with high availability:

### Step 1: Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-username/url-shortener.git
cd url-shortener

# Create production environment file
cp .env.example .env

# Edit production environment variables
nano .env
```

### Step 2: Environment Variables Configuration
```bash
# .env file for production
ENVIRONMENT=production
DOMAIN=YOUR_DOMAIN
BASE_URL=https://YOUR_DOMAIN

# Database
POSTGRES_PASSWORD=your-super-secure-database-password
DATABASE_URL=postgresql://urluser:your-super-secure-database-password@postgres:5432/url_shortener

# Security Keys (GENERATE NEW ONES!)
SECRET_KEY=your-super-secret-key-min-32-characters
API_KEY=your-api-key-for-authentication

# External Services
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
REDIS_URL=redis://redis:6379/0

# CORS
ALLOWED_ORIGINS=https://YOUR_DOMAIN,https://www.YOUR_DOMAIN

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Step 3: SSL Certificate Setup
```bash
# Create SSL directory
mkdir -p ssl

# Option A: Let's Encrypt (automated)
./scripts/setup-ssl.sh YOUR_DOMAIN

# Option B: Manual certificate placement
cp /path/to/YOUR_DOMAIN.crt ./ssl/
cp /path/to/YOUR_DOMAIN.key ./ssl/
```

### Step 4: Deploy with Docker Compose
```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f app
```

### Step 5: Verify Deployment
```bash
# Check health endpoint
curl -k https://YOUR_DOMAIN/api/health

# Test URL shortening (replace YOUR_API_KEY and YOUR_DOMAIN)
curl -X POST "https://YOUR_DOMAIN/api/shorten" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"url": "https://example.com"}'

# Test redirect
curl -I https://YOUR_DOMAIN/SHORTENED_CODE
```

## Security Checklist

### ✅ Production Security
- [ ] SSL/TLS certificates installed and configured
- [ ] Strong, unique API keys generated
- [ ] Database password is secure (20+ characters)
- [ ] Secret key is unique and secure (32+ characters)
- [ ] Sentry configured for error tracking
- [ ] Rate limiting enabled and configured
- [ ] CORS properly configured for your domain only
- [ ] Nginx security headers enabled
- [ ] Docker containers running as non-root user
- [ ] Database not exposed to external network
- [ ] Regular security updates scheduled

### 🔒 Firewall Configuration
```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Monitoring & Maintenance

### 📊 Health Monitoring
```bash
# Health check endpoint
GET /api/health

# Metrics endpoint (requires API key)
GET /api/metrics
```

### 🔍 Log Management
```bash
# Application logs
docker-compose -f docker-compose.prod.yml logs app

# Database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Nginx logs
docker-compose -f docker-compose.prod.yml logs nginx
```

### 📈 Performance Monitoring
- **Sentry**: Error tracking and performance monitoring
- **Health Checks**: Automated health monitoring via `/api/health`
- **Metrics**: Basic metrics available at `/api/metrics`

### 🔄 Updates & Backups
```bash
# Database backup
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U urluser url_shortener > backup_$(date +%Y%m%d).sql

# Application update
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Database restore (if needed)
docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U urluser url_shortener < backup_YYYYMMDD.sql
```

## Troubleshooting

### Common Issues

#### SSL Certificate Issues
```bash
# Verify certificate
openssl x509 -in ssl/YOUR_DOMAIN.crt -text -noout

# Check certificate expiry
openssl x509 -in ssl/YOUR_DOMAIN.crt -dates -noout
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose -f docker-compose.prod.yml exec postgres psql -U urluser -d url_shortener -c "SELECT 1;"

# Reset database (CAUTION: This deletes all data)
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Scale application (if needed)
docker-compose -f docker-compose.prod.yml up -d --scale app=3
```

## Cost Optimization

### Server Sizing Guidelines

#### 💸 **Ultra-Budget (Personal Use)**
- **Specs**: 512MB RAM, 1 CPU, 10GB storage
- **Cost**: $3-5/month (Linode Nanode, DO Basic)
- **Capacity**: ~100 URLs/day, ~1,000 total URLs
- **Deployment**: SQLite + single Python process

#### 💰 **Budget-Friendly (Small Business)**  
- **Specs**: 1GB RAM, 1 CPU, 25GB storage
- **Cost**: $5-10/month (Most basic VPS)
- **Capacity**: ~1,000 URLs/day, ~100,000 total URLs
- **Deployment**: SQLite or lightweight PostgreSQL

#### 🏢 **Standard Production**
- **Specs**: 2GB RAM, 2 CPU, 50GB storage  
- **Cost**: $10-20/month
- **Capacity**: ~10,000 URLs/day, ~1M total URLs
- **Deployment**: Full Docker stack with PostgreSQL

#### 🚀 **High Performance**
- **Specs**: 4GB+ RAM, 4+ CPU, 100GB+ storage
- **Cost**: $20+/month
- **Capacity**: 100,000+ URLs/day, unlimited scale
- **Deployment**: Multi-instance with load balancing

### 📊 **Quick Comparison**

| Deployment Type | Monthly Cost | Setup Time | Maintenance | Best For |
|----------------|-------------|------------|-------------|----------|
| Lightweight | $3-5 | 15 mins | Minimal | Personal projects |
| Docker Production | $10-20 | 30 mins | Medium | Small business |
| High Performance | $20+ | 1 hour | High | Enterprise |

### CDN Integration (Optional)
Consider CloudFlare for:
- Global content distribution
- DDoS protection
- Additional SSL termination
- Advanced caching

---

## 🆘 Emergency Contacts & Support

- **Application Logs**: Check Sentry dashboard
- **Server Issues**: Monitor health endpoints
- **SSL Problems**: Verify certificate validity
- **Database Issues**: Check PostgreSQL logs

**Deployment successful!** Your URL shortener should now be live at https://YOUR_DOMAIN

---

## 📋 Quick Example

For a domain like `example.com`, you would:

```bash
# 1. Quick setup (recommended)
./scripts/setup-domain.sh example.com

# 2. Set up DNS records
A     example.com         → 192.168.1.100
A     www.example.com     → 192.168.1.100

# 3. Deploy
DOMAIN=example.com docker-compose -f docker-compose.prod.yml up -d

# 4. Test
curl https://example.com/api/health
```
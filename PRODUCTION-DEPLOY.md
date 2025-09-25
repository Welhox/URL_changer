# Production Deployment Guide

## Domain Setup

Your URL shortener will have this structure:

- **`https://yourdomain.com/`** → Frontend (React app)  
- **`https://yourdomain.com/abc123`** → Shortened URL redirects
- **`https://yourdomain.com/api/shorten`** → API endpoints
- **`https://yourdomain.com/api/health`** → Health check

## Pre-deployment Steps

### 1. Update Environment Variables

Edit `.env.production` with your actual domain:

```bash
ENVIRONMENT=production
DOMAIN=yourdomain.com
BASE_URL=https://yourdomain.com

DATABASE_URL=postgresql://postgres:CB1Xa6f1kabeyTI8@db.pqcgnkdmcarlfewfqidq.supabase.co:5432/postgres

SECRET_KEY=arNgJAJLTp1h%zWP2LRe#FqtGyhpotlpMbsl%YL0tuZtu0V8K2Badh%76Fwovvc2
API_KEY=JCffTVvDzYiOUqTFrJmTNAMa9ql6kcvC

ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

RATE_LIMIT_PER_MINUTE=30
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
LOG_LEVEL=INFO
```

### 2. Update Frontend Environment

The `frontend/.env.production` should already be configured correctly:

```bash
VITE_API_BASE_URL=""
VITE_API_KEY=JCffTVvDzYiOUqTFrJmTNAMa9ql6kcvC
```

## Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up --build -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f app

# Stop
docker-compose -f docker-compose.prod.yml down
```

### Option 2: Manual Docker Build

```bash
# Build the image
docker build -t url-shortener .

# Run with environment file
docker run -d \
  --name url-shortener \
  --env-file .env.production \
  -p 8000:8000 \
  url-shortener
```

## Platform-Specific Deployment

### Railway
1. Connect your GitHub repository
2. Add environment variables from `.env.production`
3. Deploy automatically

### DigitalOcean App Platform
1. Create new app from GitHub repository
2. Set environment variables
3. Deploy with Docker

### Google Cloud Run
```bash
# Build and push to Google Container Registry
docker build -t gcr.io/PROJECT_ID/url-shortener .
docker push gcr.io/PROJECT_ID/url-shortener

# Deploy to Cloud Run
gcloud run deploy url-shortener \
  --image gcr.io/PROJECT_ID/url-shortener \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "$(cat .env.production | xargs)"
```

### AWS Fargate
Use the provided `docker-compose.prod.yml` with AWS ECS.

## Domain Configuration

### DNS Settings
Point your domain to your hosting provider:

```
A Record: @ → YOUR_SERVER_IP
CNAME: www → yourdomain.com
```

### SSL Certificate
Most platforms (Railway, DigitalOcean, etc.) provide automatic SSL.

For manual setup with Let's Encrypt:
```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Post-deployment Testing

### 1. Health Check
```bash
curl https://yourdomain.com/api/health
```

### 2. Create Short URL
```bash
curl -X POST "https://yourdomain.com/api/shorten" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"url": "https://example.com"}'
```

### 3. Test Redirect
Visit the returned short URL in browser.

### 4. Frontend Access
Visit `https://yourdomain.com` to see the frontend.

## Monitoring

### Health Endpoint
```bash
curl https://yourdomain.com/api/health
```

### Metrics (with API key)
```bash
curl -H "X-API-Key: YOUR_API_KEY" https://yourdomain.com/api/metrics
```

## Troubleshooting

### Container Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f app
```

### Database Connection
Verify Supabase connection in logs.

### Static Files
Ensure frontend builds successfully and static files are copied to `/app/static/` in container.

## Security Checklist

- ✅ Strong SECRET_KEY and API_KEY
- ✅ HTTPS enabled  
- ✅ Rate limiting configured
- ✅ CORS origins restricted to your domain
- ✅ API key required in production
- ✅ Database connection secured

## Backup

Your database is hosted on Supabase, so backups are handled automatically. For additional security, you can:

1. Export database periodically
2. Store environment variables securely
3. Version control your deployment configuration

---

🚀 **Your URL shortener is now ready for production!**
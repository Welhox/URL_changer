# 🚀 Simple Google Cloud Run Deployment

## Quick Setup with GitHub Integration

### 1. **Connect GitHub to Google Cloud**
```bash
# One-time setup
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

### 2. **Set up secrets in Google Secret Manager**
```bash
# Create your secrets (do this once)
echo "your-secret-key" | gcloud secrets create SECRET_KEY --data-file=-
echo "your-database-url" | gcloud secrets create DATABASE_URL --data-file=-
echo "your-api-key" | gcloud secrets create API_KEY --data-file=-
```

### 3. **Deploy from GitHub**
- Go to Google Cloud Console → Cloud Run
- Click "Create Service"
- Choose "Deploy from repository"
- Connect your GitHub repo
- Set environment variables to use the secrets

That's it! Google Cloud will automatically deploy on every push to main.

## Manual .env Setup

Just create `.env.production` locally:
```env
SECRET_KEY=your-secret-here
DATABASE_URL=postgresql://user:pass@host:port/db
API_KEY=your-api-key
DOMAIN=your-domain.com
```

## Files You Need

- `Dockerfile` (backend) ✅ 
- `Dockerfile` (frontend) ✅
- `.gitignore` ✅
- Your .env files (not committed)

## Files You DON'T Need
- ❌ All the deployment scripts
- ❌ Complex setup scripts  
- ❌ Multiple configuration files

**Simple is better!** 🎯
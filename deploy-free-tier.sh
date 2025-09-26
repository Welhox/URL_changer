#!/bin/bash

# Ultra-Low-Cost Cloud Run Deployment 
# Optimized for free tier usage

set -e

PROJECT_ID="your-project-id"
REGION="us-central1"  # Cheapest region
SERVICE_BACKEND="url-shortener-backend"
SERVICE_FRONTEND="url-shortener-frontend"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🆓 Deploying with FREE TIER optimization...${NC}"

# Set project
gcloud config set project ${PROJECT_ID}

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

echo -e "${GREEN}💡 Free tier optimizations enabled:${NC}"
echo "- Minimum CPU allocation"
echo "- Scales to zero when idle"
echo "- Optimized memory usage"
echo "- Single region deployment"

# Deploy backend with FREE TIER settings
echo -e "${YELLOW}🏗️ Deploying backend (FREE tier optimized)...${NC}"
gcloud builds submit ./backend --tag gcr.io/${PROJECT_ID}/${SERVICE_BACKEND}

gcloud run deploy ${SERVICE_BACKEND} \
    --image gcr.io/${PROJECT_ID}/${SERVICE_BACKEND} \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars ENVIRONMENT=production \
    --set-secrets DATABASE_URL=database-url:latest \
    --set-secrets SECRET_KEY=secret-key:latest \
    --memory 128Mi \
    --cpu 0.08 \
    --min-instances 0 \
    --max-instances 3 \
    --timeout 60 \
    --concurrency 80 \
    --cpu-throttling

BACKEND_URL=$(gcloud run services describe ${SERVICE_BACKEND} --region ${REGION} --format 'value(status.url)')

# Deploy frontend with FREE TIER settings  
echo -e "${YELLOW}🎨 Deploying frontend (FREE tier optimized)...${NC}"
gcloud builds submit ./frontend --tag gcr.io/${PROJECT_ID}/${SERVICE_FRONTEND}

gcloud run deploy ${SERVICE_FRONTEND} \
    --image gcr.io/${PROJECT_ID}/${SERVICE_FRONTEND} \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 64Mi \
    --cpu 0.08 \
    --min-instances 0 \
    --max-instances 2 \
    --timeout 30 \
    --concurrency 100 \
    --cpu-throttling

FRONTEND_URL=$(gcloud run services describe ${SERVICE_FRONTEND} --region ${REGION} --format 'value(status.url)')

echo -e "${GREEN}🎉 FREE TIER deployment complete!${NC}"
echo -e "${GREEN}Frontend: ${FRONTEND_URL}${NC}"
echo -e "${GREEN}Backend:  ${BACKEND_URL}${NC}"

echo -e "${BLUE}📊 Expected monthly costs:${NC}"
echo "• Low traffic (< 1000 visits): $0.00/month"
echo "• Medium traffic (< 10k visits): $0.00/month" 
echo "• High traffic (< 100k visits): $1-3/month"
echo ""
echo -e "${GREEN}✅ Your URL shortener should run completely FREE! ${NC}"
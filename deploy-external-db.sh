#!/bin/bash

# Google Cloud Run Deployment Script - External Database Version
# Use this when you have an existing database hosted elsewhere

set -e

# Configuration
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_BACKEND="url-shortener-backend"
SERVICE_FRONTEND="url-shortener-frontend"

# Your external database connection string
# Example: "postgresql://username:password@your-db-host:5432/database_name"
EXTERNAL_DATABASE_URL="postgresql://username:password@your-db-host:5432/urlshortener"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying to Cloud Run with external database...${NC}"

# Check if user is logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Please login: gcloud auth login${NC}"
    exit 1
fi

# Set project
echo -e "${YELLOW}📋 Setting project to ${PROJECT_ID}...${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs (no SQL admin needed)
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create secrets for external database
echo -e "${YELLOW}🔐 Creating secrets for external database...${NC}"
echo "Creating secrets in Google Secret Manager..."

# You'll need to run these commands with your actual values:
echo -e "${GREEN}Run these commands with your actual values:${NC}"
echo "echo 'your-jwt-secret-key-here' | gcloud secrets create secret-key --data-file=-"
echo "echo '${EXTERNAL_DATABASE_URL}' | gcloud secrets create database-url --data-file=-"
echo "echo 'your-api-key-here' | gcloud secrets create api-key --data-file=-"
echo ""
echo -e "${YELLOW}Press Enter after you've created the secrets...${NC}"
read -p ""

# Build and deploy backend
echo -e "${YELLOW}🏗️ Building backend...${NC}"
gcloud builds submit ./backend --tag gcr.io/${PROJECT_ID}/${SERVICE_BACKEND}

echo -e "${YELLOW}🚀 Deploying backend...${NC}"
gcloud run deploy ${SERVICE_BACKEND} \
    --image gcr.io/${PROJECT_ID}/${SERVICE_BACKEND} \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars ENVIRONMENT=production \
    --set-secrets SECRET_KEY=secret-key:latest \
    --set-secrets DATABASE_URL=database-url:latest \
    --set-secrets API_KEY=api-key:latest \
    --memory 512Mi \
    --cpu 1000m \
    --max-instances 10 \
    --timeout 300

# Get backend URL
BACKEND_URL=$(gcloud run services describe ${SERVICE_BACKEND} --region ${REGION} --format 'value(status.url)')
echo -e "${GREEN}✅ Backend deployed at: ${BACKEND_URL}${NC}"

# Build and deploy frontend
echo -e "${YELLOW}🎨 Building frontend...${NC}"
gcloud builds submit ./frontend --tag gcr.io/${PROJECT_ID}/${SERVICE_FRONTEND}

echo -e "${YELLOW}🚀 Deploying frontend...${NC}"
gcloud run deploy ${SERVICE_FRONTEND} \
    --image gcr.io/${PROJECT_ID}/${SERVICE_FRONTEND} \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 1000m \
    --max-instances 5 \
    --timeout 60

FRONTEND_URL=$(gcloud run services describe ${SERVICE_FRONTEND} --region ${REGION} --format 'value(status.url)')

echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo -e "${GREEN}Frontend: ${FRONTEND_URL}${NC}"
echo -e "${GREEN}Backend:  ${BACKEND_URL}${NC}"

echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Test your application at ${FRONTEND_URL}"
echo "2. Update your external database firewall to allow Cloud Run IPs"
echo "3. Configure custom domain (optional)"
echo "4. Set up monitoring"

echo -e "${YELLOW}⚠️ Important:${NC}"
echo "Make sure your external database allows connections from Cloud Run."
echo "You may need to whitelist Google Cloud IP ranges."
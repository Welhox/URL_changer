#!/bin/bash

# Google Cloud Run Deployment Script
# Run this script to deploy your URL shortener to Google Cloud Run

set -e

# Configuration
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_BACKEND="url-shortener-backend"
SERVICE_FRONTEND="url-shortener-frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Google Cloud Run deployment...${NC}"

# Check if user is logged in to gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Not logged in to gcloud. Please run: gcloud auth login${NC}"
    exit 1
fi

# Set project
echo -e "${YELLOW}📋 Setting project to ${PROJECT_ID}...${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Create secrets (you'll need to set these)
echo -e "${YELLOW}🔐 Creating secrets...${NC}"
echo "Please create the following secrets in Google Secret Manager:"
echo "1. secret-key: A random string for JWT tokens"
echo "2. database-url: PostgreSQL connection string"
echo "3. api-key: API key for production"

# Build and deploy backend
echo -e "${YELLOW}🏗️ Building and deploying backend...${NC}"
gcloud builds submit ./backend --tag gcr.io/${PROJECT_ID}/${SERVICE_BACKEND}

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
    --max-instances 10

# Get backend URL
BACKEND_URL=$(gcloud run services describe ${SERVICE_BACKEND} --region ${REGION} --format 'value(status.url)')
echo -e "${GREEN}✅ Backend deployed at: ${BACKEND_URL}${NC}"

# Build and deploy frontend
echo -e "${YELLOW}🎨 Building and deploying frontend...${NC}"
# Update frontend environment variables
export VITE_API_BASE_URL=${BACKEND_URL}

gcloud builds submit ./frontend --tag gcr.io/${PROJECT_ID}/${SERVICE_FRONTEND}

gcloud run deploy ${SERVICE_FRONTEND} \
    --image gcr.io/${PROJECT_ID}/${SERVICE_FRONTEND} \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 1000m \
    --max-instances 5

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe ${SERVICE_FRONTEND} --region ${REGION} --format 'value(status.url)')

echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo -e "${GREEN}Frontend: ${FRONTEND_URL}${NC}"
echo -e "${GREEN}Backend:  ${BACKEND_URL}${NC}"

echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Set up Cloud SQL PostgreSQL instance"
echo "2. Update database connection string in Secret Manager"
echo "3. Configure custom domain (optional)"
echo "4. Set up monitoring and logging"
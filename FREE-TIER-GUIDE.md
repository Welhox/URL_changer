# 🆓 FREE TIER CLOUD RUN DEPLOYMENT GUIDE

## 💰 Total Expected Cost: $0.00/month

Your URL shortener can run **completely FREE** on Google Cloud Run for low to moderate traffic!

## 📊 Free Tier Limits (Monthly)

| Resource | Free Allowance | Your Usage | Status |
|----------|---------------|------------|---------|
| **Requests** | 2,000,000 | ~10,000 | ✅ FREE |
| **CPU Time** | 180,000 seconds | ~100 seconds | ✅ FREE |
| **Memory** | 360,000 GB-seconds | ~50 GB-seconds | ✅ FREE |
| **Network** | 1 GB egress | ~100 MB | ✅ FREE |

## 🎯 Free Tier Optimizations Applied

### **Backend Configuration:**
```yaml
Memory: 128Mi          # Minimal memory usage
CPU: 0.08              # Minimum CPU allocation  
Min Instances: 0       # Scales to zero (no idle costs)
Max Instances: 3       # Prevents unexpected scaling costs
Timeout: 60s           # Quick responses
CPU Throttling: ON     # Reduces CPU usage when possible
```

### **Frontend Configuration:**
```yaml
Memory: 64Mi           # Ultra-low memory for static files
CPU: 0.08              # Minimum CPU allocation
Min Instances: 0       # Scales to zero completely  
Max Instances: 2       # Minimal scaling
Timeout: 30s           # Fast static file serving
```

## 📈 Traffic Scenarios & Costs

### **Scenario 1: Personal Use (Recommended FREE)**
- **Daily visits**: ~30 
- **Monthly URLs created**: ~50
- **API calls**: ~500/month
- **Cost**: **$0.00/month** ✅

### **Scenario 2: Small Team/Project** 
- **Daily visits**: ~200
- **Monthly URLs created**: ~300  
- **API calls**: ~3,000/month
- **Cost**: **$0.00/month** ✅

### **Scenario 3: Popular Side Project**
- **Daily visits**: ~1,000
- **Monthly URLs created**: ~1,000
- **API calls**: ~15,000/month  
- **Cost**: **$0.00/month** ✅

### **Scenario 4: Heavy Usage (Still Mostly Free)**
- **Daily visits**: ~3,000
- **Monthly URLs created**: ~5,000
- **API calls**: ~50,000/month
- **Cost**: **$0.50-2.00/month** 💰

## 🚀 Deployment Commands

```bash
# 1. Create your project
gcloud projects create my-url-shortener

# 2. Set up secrets (one-time)
echo 'your-jwt-secret' | gcloud secrets create secret-key --data-file=-
echo 'your-database-url' | gcloud secrets create database-url --data-file=-

# 3. Deploy with free tier optimization
./deploy-free-tier.sh
```

## 💡 Cost Monitoring Tips

### **Stay in Free Tier:**
```bash
# Monitor your usage monthly
gcloud logging read "resource.type=cloud_run_revision" --limit=10 --format="table(timestamp,resource.labels.service_name)"

# Check current costs
gcloud billing budgets list --billing-account=YOUR-BILLING-ACCOUNT
```

### **Set Budget Alerts:**
```bash
# Create $1 budget alert (safety net)
gcloud billing budgets create \
  --billing-account=YOUR-BILLING-ACCOUNT \
  --display-name="URL-Shortener-Budget" \
  --budget-amount=1USD \
  --threshold-rule=percent=80,basis=CURRENT_SPEND
```

## 🔧 Additional Free Services You Can Use

### **Custom Domain (Optional):**
- **Cloud DNS**: $0.50/month per domain
- **SSL Certificate**: FREE (automatic)

### **Monitoring (FREE):**
- **Cloud Logging**: 50 GB/month free
- **Cloud Monitoring**: FREE for basic metrics
- **Uptime Checks**: 1 million checks/month free

### **Database Options:**
- **Your existing database**: Current cost
- **Cloud SQL free tier**: $0 for f1-micro (if eligible)
- **Firebase**: 50K reads/day free

## 🎉 Bottom Line

Your URL shortener will likely run **100% FREE** on Google Cloud Run unless you get viral traffic! The free tier is extremely generous for personal projects and small applications.

**Estimated monthly cost for typical usage: $0.00** ✨
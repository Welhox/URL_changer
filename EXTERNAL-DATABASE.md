# External Database Configuration for Cloud Run

## 🗄️ Using Your Existing Database

You can keep your database wherever it's currently hosted (DigitalOcean, AWS RDS, Heroku, etc.) and just deploy the application to Cloud Run.

## 🔧 Required Configuration

### **1. Database Connection String**
Your external database URL should be in this format:
```
postgresql://username:password@hostname:port/database_name
```

### **2. Firewall Configuration**
Your database host needs to allow connections from Google Cloud Run. 

**Options:**
- **Option A**: Allow all IPs (0.0.0.0/0) - Simple but less secure
- **Option B**: Whitelist Google Cloud IP ranges - More secure

### **3. Google Cloud IP Ranges**
If you want to whitelist specific IPs, get the current ranges:
```bash
# Get Google Cloud IP ranges
curl -s https://www.gstatic.com/ipranges/cloud.json | jq '.prefixes[] | select(.scope=="us-central1") | .ipv4Prefix'
```

## 🚀 Deployment Steps

### **Step 1: Prepare Secrets**
```bash
# Create your secrets (run these with your actual values)
echo 'your-secret-jwt-key' | gcloud secrets create secret-key --data-file=-
echo 'postgresql://user:pass@host:5432/db' | gcloud secrets create database-url --data-file=-  
echo 'your-api-key' | gcloud secrets create api-key --data-file=-
```

### **Step 2: Deploy Application**
```bash
# Use the external database deployment script
./deploy-external-db.sh
```

### **Step 3: Test Connection**
```bash
# Test if Cloud Run can reach your database
gcloud run jobs create db-test \
    --image gcr.io/google.com/cloudsdktool/cloud-sdk \
    --set-secrets DATABASE_URL=database-url:latest \
    --command psql \
    --args '$DATABASE_URL -c "SELECT 1;"'
```

## 💰 Cost Comparison

### **External Database (Keep Current)**
- **Application**: $10-25/month (Cloud Run)
- **Database**: Current hosting cost
- **Total**: Current cost + $10-25/month

### **Cloud SQL Migration**  
- **Application**: $10-25/month (Cloud Run)
- **Database**: $15-50/month (Cloud SQL)
- **Total**: $25-75/month

## 🔒 Security Considerations

### **External Database Pros:**
✅ No data migration risks
✅ Keep existing backup strategy  
✅ Potentially lower costs
✅ Geographic flexibility

### **External Database Cons:**
❌ Network latency (if far from Cloud Run)
❌ Need to manage database firewall
❌ Less integration with Google Cloud monitoring

### **Cloud SQL Pros:**
✅ Tight integration with Cloud Run
✅ Built-in backups and monitoring
✅ Better performance (same network)
✅ Automatic security patches

### **Cloud SQL Cons:**
❌ Migration complexity
❌ Potentially higher costs
❌ Vendor lock-in

## 🎯 Recommendation

**Keep your external database if:**
- It's reliable and fast
- Cost is significantly lower
- You have good backup procedures
- Migration seems risky

**Consider Cloud SQL if:**
- You want full Google Cloud integration
- Your current database has performance issues
- You want automated backups and monitoring
- Cost difference is minimal
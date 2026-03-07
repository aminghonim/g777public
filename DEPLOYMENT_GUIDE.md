# G777 Cloud Deployment Setup Guide
# ==================================

## Prerequisites
1. GitHub repository with code
2. Google Cloud Project (whatsapp-pairing-service)
3. Billing enabled
4. GitHub secrets configured

## Step 1: Create Google Cloud Secrets

```bash
# Create DATABASE_URL secret
echo -n "postgresql://neondb_owner:npg_Y7gnvIXyTBe5@ep-sweet-wildflower-a854ps51-pooler.eastus2.azure.neon.tech/neondb?sslmode=require" | \
  gcloud secrets create DATABASE_URL --data-file=- --project=whatsapp-pairing-service

# Create GEMINI_API_KEY secret  
echo -n "AIzaSyDBrn8vJ3k1Xu86VhdNHSse9ybbJyxDG2g" | \
  gcloud secrets create GEMINI_API_KEY --data-file=- --project=whatsapp-pairing-service
```

## Step 2: Grant Cloud Run Access to Secrets

```bash
# Get the Cloud Run service account
PROJECT_NUMBER=$(gcloud projects describe whatsapp-pairing-service --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant secret accessor role
gcloud secrets add-iam-policy-binding DATABASE_URL \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

## Step 3: Create Artifact Registry Repository

```bash
gcloud artifacts repositories create g777-backend \
  --repository-format=docker \
  --location=europe-west1 \
  --description="G777 Smart CRM Backend" \
  --project=whatsapp-pairing-service
```

## Step 4: Configure GitHub Secrets

Go to GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `GCP_CREDENTIALS`: Service account JSON key
- `BAILEYS_API_URL`: https://baileys-service-748303506355.europe-west1.run.app

## Step 5: Deploy

```bash
# Push to main branch
git add .
git commit -m "Deploy G777 to Cloud Run"
git push origin main
```

GitHub Actions will automatically build and deploy!

## Manual Deployment (Alternative)

```bash
# Build locally
docker build -t europe-west1-docker.pkg.dev/whatsapp-pairing-service/g777-backend/g777-backend:latest .

# Push
docker push europe-west1-docker.pkg.dev/whatsapp-pairing-service/g777-backend/g777-backend:latest

# Deploy
gcloud run deploy g777-backend \
  --image europe-west1-docker.pkg.dev/whatsapp-pairing-service/g777-backend/g777-backend:latest \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars "IS_CLOUD=true,PORT=8080,BAILEYS_API_URL=https://baileys-service-748303506355.europe-west1.run.app" \
  --set-secrets "GEMINI_API_KEY=GEMINI_API_KEY:latest,DATABASE_URL=DATABASE_URL:latest" \
  --memory 512Mi \
  --min-instances 0 \
  --max-instances 10
```

## Verification

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe g777-backend --region europe-west1 --format 'value(status.url)')

# Test health endpoint
curl $SERVICE_URL/webhook/health

# Expected response:
# {"status": "healthy", "service": "G777 Webhook Handler", "ai_engine": "online", "database": "connected"}
```

## Troubleshooting

### Check logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=g777-backend" --limit 50
```

### Update secrets
```bash
echo -n "new_value" | gcloud secrets versions add SECRET_NAME --data-file=-
```

### Rollback
```bash
gcloud run services update-traffic g777-backend --to-revisions=PREVIOUS_REVISION=100
```

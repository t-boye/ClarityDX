# ClarityDx - Netlify Deployment Guide

This guide explains how to deploy the ClarityDx Multi-Disease Diagnosis System to Netlify with serverless backend functions.

## Overview

The application has been migrated to a Netlify-compatible architecture:
- **Frontend**: React + Vite static build
- **Backend**: Python Netlify serverless functions
- **Database**: PostgreSQL (hosted separately)
- **ML Models**: Loaded from AWS S3

## Project Structure

```
ClarityDx/
├── frontend/                 # React frontend application
│   ├── src/                  # React source code
│   ├── netlify/              # Netlify serverless functions
│   │   └── functions/        # Serverless backend functions
│   │       ├── requirements.txt
│   │       ├── shared/       # Shared utilities and modules
│   │       │   ├── utils/    # Database utilities
│   │       │   ├── prediction/  # ML prediction modules
│   │       │   ├── services/ # Image processing services
│   │       │   ├── model_config.py
│   │       │   └── model_loader.py
│   │       │
│   │       ├── predict-heart-disease.py
│   │       ├── predict-ckd.py
│   │       ├── predict-hepatitis-c.py
│   │       ├── predict-symscan.py
│   │       ├── process-malaria-image.py
│   │       ├── patients.py
│   │       ├── encounters.py
│   │       └── records.py
│   │
│   ├── package.json
│   └── vite.config.js
│
├── backend/                  # Legacy Flask backend (for reference)
└── netlify.toml             # Netlify configuration

```

## Serverless Functions

### Prediction Endpoints

| Endpoint | Function File | Description |
|----------|--------------|-------------|
| `/api/predict/heart_disease` | `predict-heart-disease.py` | Heart disease prediction |
| `/api/predict/ckd` | `predict-ckd.py` | Chronic kidney disease prediction |
| `/api/predict/hepatitis_c` | `predict-hepatitis-c.py` | Hepatitis C prediction |
| `/api/predict/symscan` | `predict-symscan.py` | Symptom-based disease prediction |
| `/api/image-processing/process-image` | `process-malaria-image.py` | Malaria diagnosis from blood cell images |

### Patient Management Endpoints

| Endpoint | Function File | Method | Description |
|----------|--------------|--------|-------------|
| `/api/patients` | `patients.py` | GET | List all patients |
| `/api/patients` | `patients.py` | POST | Create new patient |
| `/api/patients/:id` | `patients.py` | GET | Get patient by ID |
| `/api/patients/:id` | `patients.py` | PUT | Update patient |
| `/api/patients/:id` | `patients.py` | DELETE | Delete patient |
| `/api/patients/:id/encounters` | `encounters.py` | GET | List patient encounters |
| `/api/patients/:id/encounters` | `encounters.py` | POST | Create encounter |
| `/api/encounters/:id` | `encounters.py` | GET/PUT/DELETE | Manage encounters |
| `/api/encounters/:id/records` | `records.py` | GET/POST | Manage records |
| `/api/records/:id` | `records.py` | GET/PUT/DELETE | Manage individual records |

## Prerequisites

Before deploying, ensure you have:

1. **Netlify Account**: Sign up at https://netlify.com
2. **PostgreSQL Database**: Set up a hosted PostgreSQL instance (recommended: Supabase, Neon, or Render)
3. **AWS S3 Access**: ML models are hosted on S3 (already configured)
4. **Firebase Project**: For authentication (already configured)

## Environment Variables

### Required Environment Variables

Configure these in the Netlify dashboard under **Site settings → Environment variables**:

#### Database Configuration
```
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432
DATABASE_URL=postgresql://user:password@host:5432/database
```

#### Frontend Variables (VITE_*)
```
VITE_API_BASE_URL=/.netlify/functions
VITE_FIREBASE_API_KEY=AIzaSyAci2wbrmgtwNpJe1RmiInRodoYN3yxSM8
VITE_FIREBASE_AUTH_DOMAIN=expert-system-12901.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=expert-system-12901
VITE_FIREBASE_STORAGE_BUCKET=expert-system-12901.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=1097631977674
VITE_FIREBASE_APP_ID=1:1097631977674:web:d41d67259f50d42af72433
```

#### AWS Credentials (for ML model loading)
```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

## Deployment Steps

### Option 1: Deploy via Netlify Dashboard (Recommended)

1. **Connect Repository**
   - Go to https://app.netlify.com
   - Click "Add new site" → "Import an existing project"
   - Connect to your GitHub repository
   - Select the `ClarityDx` repository

2. **Configure Build Settings**
   - **Base directory**: `frontend/`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
   - **Functions directory**: `netlify/functions`

3. **Add Environment Variables**
   - Go to **Site settings → Environment variables**
   - Add all variables listed in the "Required Environment Variables" section above
   - Click "Save"

4. **Deploy**
   - Click "Deploy site"
   - Netlify will build and deploy your application
   - First deployment may take 5-10 minutes due to Python dependencies

### Option 2: Deploy via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Navigate to project root
cd ClarityDx

# Login to Netlify
netlify login

# Initialize Netlify site
netlify init

# Deploy
netlify deploy --prod
```

## Database Setup

### PostgreSQL Schema

Your PostgreSQL database needs the following tables:

```sql
-- Patients table
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    unique_patient_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(50),
    contact_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Encounters table
CREATE TABLE encounters (
    encounter_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(patient_id) ON DELETE CASCADE,
    encounter_date DATE,
    encounter_time TIME,
    chief_complaint TEXT,
    notes TEXT,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Records table
CREATE TABLE records (
    record_id SERIAL PRIMARY KEY,
    encounter_id INTEGER REFERENCES encounters(encounter_id) ON DELETE CASCADE,
    record_date DATE NOT NULL,
    details TEXT NOT NULL,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Recommended Database Providers

1. **Supabase** (Free tier available)
   - Go to https://supabase.com
   - Create a new project
   - Get connection string from Settings → Database
   - Use connection pooler URL for better serverless compatibility

2. **Neon** (Serverless PostgreSQL)
   - Go to https://neon.tech
   - Create project
   - Get connection string

3. **Render** (Free tier available)
   - Go to https://render.com
   - Create PostgreSQL database
   - Get connection string

## Post-Deployment

### 1. Verify Deployment

After deployment, test the following:

✅ Frontend loads correctly
✅ API endpoints respond (check Network tab in browser DevTools)
✅ Database connections work
✅ ML model predictions function
✅ Image upload works for malaria diagnosis

### 2. Check Function Logs

Monitor serverless function logs in Netlify dashboard:
- **Functions tab** → Select a function → View logs
- Look for errors related to:
  - Database connections
  - Model loading from S3
  - Missing environment variables

### 3. Common Issues

#### Cold Start Delays
- **Problem**: First request to a function is slow (10-30 seconds)
- **Solution**: This is normal for Python functions with TensorFlow. Subsequent requests will be faster due to caching.

#### Database Connection Issues
- **Problem**: Functions timeout or fail to connect to database
- **Solution**:
  - Verify `DATABASE_URL` is correct
  - Use connection pooling URL if available
  - Check database allows connections from Netlify IPs

#### Model Loading Failures
- **Problem**: Predictions fail with "model not available"
- **Solution**:
  - Verify S3 URLs in `netlify/functions/shared/model_config.py`
  - Check AWS credentials are set correctly
  - Increase function timeout in `netlify.toml`

#### Image Upload Issues
- **Problem**: Malaria image processing fails
- **Solution**:
  - Check function size limits (Netlify has 50MB zipped limit)
  - Verify image processing dependencies are installed

## Performance Optimization

### 1. Function Caching

Models are cached in `/tmp` directory and in-memory between warm starts. This significantly reduces cold start times.

### 2. Database Connection Pooling

The `shared/utils/db_utils.py` uses connection pooling to reuse database connections across function invocations.

### 3. Model Loading Strategy

Models are loaded on-demand and cached. First prediction request will be slow, but subsequent requests will be fast.

## Monitoring and Debugging

### Netlify Function Logs
```bash
# View live logs
netlify functions:log
```

### Check Function Performance
- Go to **Functions tab** in Netlify dashboard
- View execution time, invocation count, and error rates

## Security Considerations

⚠️ **IMPORTANT**: Remove sensitive credentials from code

1. **Remove AWS credentials from .env files**
   - The file `frontend/.env.local` currently contains exposed AWS credentials
   - These should be moved to Netlify environment variables
   - Remove them from the repository immediately

2. **Rotate Exposed Credentials**
   - If credentials were committed to git, rotate them immediately
   - Update AWS IAM keys
   - Update any other exposed secrets

3. **Database Security**
   - Use SSL connections to PostgreSQL
   - Restrict database access to Netlify IPs if possible
   - Use strong passwords

## Scaling Considerations

### Function Limits
- **Execution time**: 10 seconds (26 seconds for background functions)
- **Memory**: 1024 MB
- **Payload size**: 6 MB

If you encounter these limits:
1. Optimize model loading (use smaller models)
2. Use background functions for long-running predictions
3. Consider caching prediction results

## Cost Estimation

### Netlify Costs
- **Free tier**: 125,000 function invocations/month
- **Pro tier**: $19/month + overages
- **Bandwidth**: 100 GB/month on free tier

### Database Costs
- **Supabase**: Free tier (500 MB database, 2GB bandwidth)
- **Neon**: Free tier (0.5 GB storage)
- **Render**: Free tier (90 days, then $7/month)

## Troubleshooting

### Functions not deploying
```bash
# Check build logs in Netlify dashboard
# Common issues:
# - Missing requirements.txt
# - Python version mismatch
# - Import errors
```

### Database connection failures
```bash
# Test connection locally
psycopg2.connect(os.environ['DATABASE_URL'])
```

### Model loading timeouts
```bash
# Increase timeout in netlify.toml
[functions]
  external_node_modules = ["tensorflow"]
  included_files = ["shared/**"]

[functions."predict-heart-disease"]
  timeout = 30
```

## Additional Resources

- [Netlify Functions Documentation](https://docs.netlify.com/functions/overview/)
- [Python on Netlify Functions](https://docs.netlify.com/functions/python/)
- [Netlify Environment Variables](https://docs.netlify.com/environment-variables/overview/)
- [Supabase Documentation](https://supabase.com/docs)

## Support

If you encounter issues:
1. Check Netlify function logs
2. Review this deployment guide
3. Test locally with `netlify dev`
4. Check GitHub issues for similar problems

---

**Deployment Date**: 2025-10-25
**Version**: 1.0.0
**Status**: Ready for production deployment

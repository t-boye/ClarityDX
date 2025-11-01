# Environment Variables Configuration

## Complete List of Environment Variables for Netlify

Copy and paste these into your Netlify dashboard under **Site settings → Environment variables**.

### Database Configuration

```
DB_NAME=your_postgres_database_name
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_HOST=your_postgres_host.com
DB_PORT=5432
DATABASE_URL=postgresql://user:password@host:port/database
```

**Example for Supabase:**
```
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_supabase_password
DB_HOST=db.xxxxxxxxxxxxx.supabase.co
DB_PORT=5432
DATABASE_URL=postgresql://postgres:password@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```

### Frontend Variables (Required for Vite build)

```
VITE_API_BASE_URL=/api
VITE_FIREBASE_API_KEY=AIzaSyAci2wbrmgtwNpJe1RmiInRodoYN3yxSM8
VITE_FIREBASE_AUTH_DOMAIN=expert-system-12901.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=expert-system-12901
VITE_FIREBASE_STORAGE_BUCKET=expert-system-12901.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=1097631977674
VITE_FIREBASE_APP_ID=1:1097631977674:web:d41d67259f50d42af72433
```

### AWS Credentials (Optional - for direct S3 access)

⚠️ **Note**: The ML models are currently configured to download from public S3 URLs, so these may not be required. Only add if you encounter access issues.

```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

## How to Add Environment Variables in Netlify

### Via Dashboard

1. Go to https://app.netlify.com
2. Select your site
3. Go to **Site settings**
4. Click **Environment variables** in the left sidebar
5. Click **Add a variable**
6. For each variable:
   - Enter the **Key** (e.g., `DB_NAME`)
   - Enter the **Value** (e.g., `postgres`)
   - Select scope: **All scopes** (recommended)
   - Click **Create variable**

### Via Netlify CLI

```bash
# Set a single variable
netlify env:set DB_NAME "your_database_name"

# Set all variables from a file
netlify env:import .env
```

## Environment Variables per Context

Netlify supports different variables for different deployment contexts:

- **Production**: Used for main production deployment
- **Deploy previews**: Used for pull request previews
- **Branch deploys**: Used for branch deployments

For ClarityDx, use **All scopes** or set all variables for **Production** at minimum.

## Security Best Practices

✅ **DO:**
- Use Netlify environment variables for all secrets
- Rotate credentials regularly
- Use different credentials for production and development
- Enable SSL for database connections

❌ **DON'T:**
- Commit credentials to git repository
- Share environment variables in public channels
- Use production credentials in development
- Store credentials in code files

## Local Development

For local development with Netlify Dev:

1. Create a `.env` file in the project root (already gitignored):

```bash
# .env (for local development only)
DB_NAME=your_local_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

VITE_API_BASE_URL=http://localhost:8888/.netlify/functions
VITE_FIREBASE_API_KEY=AIzaSyAci2wbrmgtwNpJe1RmiInRodoYN3yxSM8
# ... other Firebase variables
```

2. Run Netlify Dev:

```bash
netlify dev
```

This will:
- Start the Vite dev server for frontend
- Run Netlify functions locally
- Load environment variables from `.env`

## Verifying Environment Variables

After setting variables in Netlify:

1. Trigger a new deployment
2. Check function logs for any "missing environment variable" errors
3. Test API endpoints to ensure database connectivity
4. Test predictions to ensure ML models load correctly

## Troubleshooting

### Variables not loading
- **Issue**: Functions can't access environment variables
- **Solution**: Redeploy the site after adding variables

### Database connection fails
- **Issue**: `DATABASE_URL` connection error
- **Solution**:
  - Verify connection string format
  - Check database allows external connections
  - Use connection pooler URL for serverless

### Firebase errors
- **Issue**: Firebase authentication fails
- **Solution**:
  - Verify all `VITE_FIREBASE_*` variables are set
  - Check Firebase project configuration
  - Ensure variables are available during build time

### Model loading errors
- **Issue**: ML models fail to download
- **Solution**:
  - Verify S3 URLs in `model_config.py`
  - Check network connectivity
  - Increase function timeout

## Required vs Optional Variables

### ✅ Required (Application won't work without these)

- `DATABASE_URL` (or individual DB_* variables)
- All `VITE_FIREBASE_*` variables
- `VITE_API_BASE_URL`

### ⚠️ Optional (May be needed depending on configuration)

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- Individual `DB_*` variables (if using `DATABASE_URL`)

## Template for Quick Setup

```bash
# Copy this template and replace with your actual values

# Database
export DATABASE_URL="postgresql://user:password@host:5432/database"

# Firebase (Frontend)
export VITE_API_BASE_URL="/.netlify/functions"
export VITE_FIREBASE_API_KEY="your_firebase_api_key"
export VITE_FIREBASE_AUTH_DOMAIN="your-project.firebaseapp.com"
export VITE_FIREBASE_PROJECT_ID="your-project-id"
export VITE_FIREBASE_STORAGE_BUCKET="your-project.firebasestorage.app"
export VITE_FIREBASE_MESSAGING_SENDER_ID="your_sender_id"
export VITE_FIREBASE_APP_ID="your_app_id"
```

---

**Last Updated**: 2025-10-25

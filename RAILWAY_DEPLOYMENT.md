# Railway Deployment Guide for Sentinel LLM

## Prerequisites
- Railway account (https://railway.app)
- GitHub repository connected

## Step-by-Step Deployment

### 1. Create PostgreSQL Database
1. In Railway, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Wait for it to deploy
4. Go to **Variables** tab and copy the `DATABASE_URL`

### 2. Create Redis Database
1. Click **"+ New"** again
2. Select **"Database"** → **"Add Redis"**
3. Wait for it to deploy
4. Go to **Variables** tab and copy the `REDIS_URL`

### 3. Deploy Backend API Service

#### Create Service:
1. Click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose **`prachi870/SentinelLLM`**
4. Railway will create a service

#### Configure Service:
1. Go to **Settings** tab
2. In **Source** section:
   - Set **Root Directory**: `backend`
3. In **Deploy** section:
   - Clear any **Pre-deploy Command**
   - Set **Custom Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Add Environment Variables:
Go to **Variables** tab and add these:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
OPENAI_API_KEY=your_groq_or_openai_api_key_here
SECRET_KEY=your_secret_key_from_env_file
TOKEN_ENCRYPTION_KEY=your_token_encryption_key_from_env_file
ENVIRONMENT=production
WATCHER_INTERVAL_SECONDS=300
MAX_LLM_CALLS_PER_SCAN=50
PORT=8000
```

**Note:** Use the actual values from your `.env` file. Don't commit these to GitHub!

### 4. Deploy Celery Worker Service

#### Create Service:
1. Click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose **`prachi870/SentinelLLM`**

#### Configure Service:
1. Go to **Settings** tab
2. In **Source** section:
   - Set **Root Directory**: `backend`
3. In **Deploy** section:
   - Set **Custom Start Command**: `celery -A tasks.celery_app worker --queues=scans,default --concurrency=2 --loglevel=info`

#### Add Environment Variables:
Add the **SAME** environment variables as Backend API (copy from step 3)

### 5. Celery Beat Service (ALREADY EXISTS)

Your "beat" service is already created. Just ensure it has:
- **Root Directory**: `backend`
- **Start Command**: `celery -A tasks.celery_app beat --loglevel=info`
- **Same environment variables** as Backend API

### 6. Deploy Frontend Service

#### Create Service:
1. Click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose **`prachi870/SentinelLLM`**

#### Configure Service:
1. Go to **Settings** tab
2. In **Source** section:
   - Set **Root Directory**: `frontend`
3. In **Deploy** section:
   - Set **Custom Start Command**: `npm run dev -- --host 0.0.0.0 --port $PORT`

#### Add Environment Variables:
Go to **Variables** tab and add:

```
VITE_API_URL=https://[YOUR-BACKEND-SERVICE].up.railway.app
```

**Important**: Replace `[YOUR-BACKEND-SERVICE]` with your actual backend service URL from Railway.

## Final Service List

You should have **5 services** in total:

1. ✅ **Postgres** (Database)
2. ✅ **Redis** (Database)
3. ✅ **Backend API** (from GitHub, root: backend)
4. ✅ **Celery Worker** (from GitHub, root: backend)
5. ✅ **Celery Beat** (from GitHub, root: backend) - Already exists
6. ✅ **Frontend** (from GitHub, root: frontend)

## Troubleshooting

### If backend shows "uvicorn: command not found"
- Check that **Root Directory** is set to `backend`
- Railway should auto-detect Dockerfile and build properly
- Check logs for build errors

### If backend crashes on startup
- Verify all environment variables are set correctly
- Check that DATABASE_URL and REDIS_URL are linked properly: `${{Postgres.DATABASE_URL}}`
- Look at the logs for specific error messages

### If frontend can't connect to backend
- Make sure `VITE_API_URL` in frontend points to the backend's public URL
- Check CORS settings in backend (main.py)

## After Deployment

1. **Get Frontend URL**: Go to frontend service → Settings → copy the public URL
2. **Test the app**: Open the frontend URL in your browser
3. **Check logs**: Monitor all services for any errors

## Important Notes

- Railway automatically redeploys when you push to GitHub
- Database URLs are automatically provided by Railway
- Make sure all services are in the **same project** so they can reference each other
- The `${{Service.VARIABLE}}` syntax only works within the same Railway project

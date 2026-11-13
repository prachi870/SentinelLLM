# Sentinel LLM - Render Deployment Guide

## Why Render?

Render is better than Railway for this project because:
- ✅ Proper worker support with dedicated process types
- ✅ Auto-configuration via `render.yaml` (Blueprint)
- ✅ Free PostgreSQL and Redis included
- ✅ Simpler environment variable management
- ✅ Better logging and monitoring

## Quick Deploy (Automatic)

1. **Go to Render**: https://render.com
2. **Sign up/Login** with your GitHub account
3. Click **"New +"** → **"Blueprint"**
4. Connect to repository: `prachi870/SentinelLLM`
5. **Blueprint Name**: `sentinel-llm`
6. Click **"Apply"**

Render will automatically:
- Create PostgreSQL database
- Create Redis instance
- Deploy web service (FastAPI)
- Deploy worker service (Celery)
- Deploy beat service (Celery Beat)
- Configure all environment variables

## After Deployment

### 1. Set API Keys

Go to each service → Environment → Add:

```bash
OPENAI_API_KEY=your_groq_or_openai_key_here
```

### 2. Get Service URLs

- **Web Service**: `https://sentinel-backend.onrender.com`
- Copy this URL for Vercel frontend configuration

### 3. Update Vercel

In Vercel project settings → Environment Variables:
```bash
VITE_API_URL=https://sentinel-backend.onrender.com
```

### 4. Create Demo User

```bash
curl -X POST https://sentinel-backend.onrender.com/api/v1/init/demo-user
```

## Manual Deploy (Alternative)

If Blueprint doesn't work, create services manually:

### 1. Create PostgreSQL Database

- Name: `sentinel-db`
- Database: `sentinelloop`
- User: `sentinel`
- Plan: Free

Copy the **Internal Database URL**

### 2. Create Redis

- Name: `sentinel-redis`
- Plan: Free

Copy the **Internal Redis URL**

### 3. Create Web Service

- **Name**: `sentinel-backend`
- **Environment**: Python 3
- **Build Command**:
  ```
  cd backend && pip install -r requirements.txt && python -m spacy download en_core_web_sm
  ```
- **Start Command**:
  ```
  cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
  ```
- **Health Check Path**: `/api/v1/health`

**Environment Variables**:
```bash
DATABASE_URL=<paste internal postgres URL>
REDIS_URL=<paste internal redis URL>
OPENAI_API_KEY=<your API key>
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
TOKEN_ENCRYPTION_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
ENVIRONMENT=production
WATCHER_INTERVAL_SECONDS=300
MAX_LLM_CALLS_PER_SCAN=50
```

### 4. Create Worker Service

- **Name**: `sentinel-worker`
- **Environment**: Python 3
- **Build Command**: Same as web service
- **Start Command**:
  ```
  cd backend && python -m celery -A tasks.celery_app worker --queues=scans,default --loglevel=info
  ```

**Environment Variables**: Same as web service (copy from web service)

### 5. Create Beat Service

- **Name**: `sentinel-beat`
- **Environment**: Python 3
- **Build Command**: Same as web service
- **Start Command**:
  ```
  cd backend && python -m celery -A tasks.celery_app beat --loglevel=info
  ```

**Environment Variables**: Same as web service

## Verification

### Check Health

```bash
curl https://sentinel-backend.onrender.com/api/v1/health
```

Should return:
```json
{"status":"ok","database":"ok","redis":"ok"}
```

### Test Login

```bash
curl -X POST https://sentinel-backend.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@sentinelloop.ai","password":"testpass123"}'
```

Should return JWT token.

## Troubleshooting

### Worker/Beat Not Starting

Check logs for `ModuleNotFoundError`. If you see it, the build command needs to run:
```
cd backend && pip install -r requirements.txt
```

### Database Connection Failed

Make sure you're using the **Internal Database URL**, not the external one. It should look like:
```
postgresql://sentinel:password@dpg-xxxxx/sentinelloop
```

### Redis Connection Failed

Use **Internal Redis URL**:
```
redis://red-xxxxx:6379
```

## Cost

Render Free Tier includes:
- ✅ 750 hours/month of web service
- ✅ PostgreSQL (90 days retention)
- ✅ Redis (25MB storage)
- ✅ Background workers (750 hours total)

Perfect for demo/testing. Upgrade to Starter ($7/month per service) for production.

## Comparison: Render vs Railway

| Feature | Render | Railway |
|---------|--------|---------|
| Worker Support | ✅ Native | ⚠️ Manual config |
| Auto-config | ✅ Blueprint | ❌ Manual only |
| Free Tier | ✅ 750hrs | ✅ $5 credit |
| Documentation | ✅ Excellent | ⚠️ Limited |
| Build Speed | ⚠️ Slower | ✅ Faster |

**Recommendation**: Use Render for this project.

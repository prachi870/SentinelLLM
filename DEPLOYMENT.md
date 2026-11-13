# Sentinel LLM - Production Deployment Guide

## Architecture

- **Frontend**: Vercel (React + Vite)
- **Backend**: Railway (FastAPI + Uvicorn)
- **Worker**: Railway (Celery worker for async scan tasks)
- **Beat**: Railway (Celery beat for scheduled tasks)
- **Database**: Railway PostgreSQL
- **Cache**: Railway Redis

## Deployment URLs

- **Frontend**: https://sentinel-llm-mehga.vercel.app
- **Backend API**: https://web-production-70282b06.up.railway.app
- **API Docs**: https://web-production-70282b06.up.railway.app/docs

## Railway Setup

### 1. Create Railway Project

1. Go to https://railway.app
2. Create new project from GitHub repo: `prachi870/SentinelLLM`
3. Railway will auto-detect the configuration files

### 2. Add Services

Create these services from the same GitHub repo:

#### Web Service (FastAPI)
- **Name**: `web`
- **Source**: GitHub `prachi870/SentinelLLM`
- **Configuration**: Uses `railway.toml` or `nixpacks.toml`
- **Start Command**: Automatically configured via `Procfile` or `railway.toml`
- **Port**: Railway assigns automatically (uses `$PORT` env var)

#### Worker Service (Celery)
- **Name**: `worker`
- **Source**: Same GitHub repo
- **Start Command**: `cd backend && python -m celery -A tasks.celery_app worker --queues=scans,default --loglevel=info`

#### Beat Service (Celery Scheduler)
- **Name**: `beat`
- **Source**: Same GitHub repo
- **Start Command**: `cd backend && python -m celery -A tasks.celery_app beat --loglevel=info`

### 3. Add Databases

#### PostgreSQL
1. Add PostgreSQL database
2. Railway automatically creates `DATABASE_URL` variable
3. Link to all three services (web, worker, beat)

#### Redis
1. Add Redis database
2. Railway automatically creates `REDIS_URL` variable
3. Link to all three services (web, worker, beat)

### 4. Environment Variables

Set these in **all three services** (web, worker, beat):

```bash
# Database (auto-created by Railway when you link PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (auto-created by Railway when you link Redis)
REDIS_URL=${{Redis.REDIS_URL}}

# OpenAI/Groq API Key
OPENAI_API_KEY=your_api_key_here

# Application secrets (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your_secret_key_here
TOKEN_ENCRYPTION_KEY=your_encryption_key_here

# Environment
ENVIRONMENT=production

# Optional: Adjust these if needed
WATCHER_INTERVAL_SECONDS=300
MAX_LLM_CALLS_PER_SCAN=50
```

## Vercel Setup

### 1. Import Project

1. Go to https://vercel.com
2. Import from GitHub: `prachi870/SentinelLLM`
3. **Root Directory**: `frontend`
4. **Framework**: Vite

### 2. Environment Variables

Add this in Vercel project settings:

```bash
VITE_API_URL=https://web-production-70282b06.up.railway.app
```

**Important**: 
- Use "Plain Text" type (not Secret) for VITE_ variables
- The value should be your Railway backend URL (without `/api/v1`)

### 3. Build Settings

Vercel auto-detects Vite configuration:
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

## Verification Checklist

After deployment, verify:

### Backend (Railway)

1. **Health Check**: `curl https://web-production-70282b06.up.railway.app/api/v1/health`
   - Should return: `{"status":"ok","database":"ok","redis":"ok"}`

2. **API Docs**: Visit `https://web-production-70282b06.up.railway.app/docs`
   - Should show interactive API documentation

3. **Services Status**:
   - `web`: ● Online
   - `worker`: ● Online  
   - `beat`: ● Online
   - `Postgres`: ● Online
   - `Redis`: ● Online

### Frontend (Vercel)

1. **Visit**: https://sentinel-llm-mehga.vercel.app
2. **Demo Login**: Click "Try Demo Login"
   - Credentials: `test@sentinelloop.ai` / `testpass123`
3. **Register Chatbot**: Add a test chatbot URL
4. **Trigger Scan**: Start a vulnerability scan
5. **Check Results**: View scan progress and findings

## Demo User

A demo user is already created in production:

- **Email**: `test@sentinelloop.ai`
- **Password**: `testpass123`
- **User ID**: `b17ae59b-e2ef-4efe-a907-2f3e3ccbd0c1`

## Troubleshooting

### Worker/Beat Services Failing

**Symptoms**: Services show "Deploy failed" or "celery: command not found"

**Fix**: Make sure you're using the correct start commands:
- Worker: `cd backend && python -m celery -A tasks.celery_app worker --queues=scans,default --loglevel=info`
- Beat: `cd backend && python -m celery -A tasks.celery_app beat --loglevel=info`

### CORS Errors

**Symptoms**: Frontend shows "blocked by CORS policy"

**Fix**: Backend uses `allow_origin_regex=r"https://.*\.vercel\.app"` which automatically allows ALL Vercel domains. If you see CORS errors:
1. Check Railway logs for the actual origin being rejected
2. Verify backend deployed successfully
3. Hard refresh browser (Ctrl+Shift+R)

### Redis Version Error

**Symptoms**: `Redis transport requires redis-py versions 6.1.0 or later`

**Fix**: Already fixed in `backend/requirements.txt`:
```
redis==6.1.0
```

### Database Connection Issues

**Symptoms**: `could not translate host name "postgres.railway.internal"`

**Fix**: Ensure `DATABASE_URL` is set to `${{Postgres.DATABASE_URL}}` (using Railway's internal reference, not a hardcoded value)

### Frontend Shows "Backend not running"

**Symptoms**: Demo login fails, API calls fail

**Checklist**:
1. Verify Railway web service is ● Online
2. Check `VITE_API_URL` is set correctly in Vercel
3. Redeploy Vercel with cache cleared
4. Hard refresh browser (Ctrl+Shift+R)

## Updating the Application

### Backend Updates

1. Push changes to GitHub main branch
2. Railway auto-deploys all services
3. Wait 2-3 minutes for deployment
4. Verify health endpoint

### Frontend Updates

1. Push changes to GitHub main branch
2. Vercel auto-deploys
3. Wait 1-2 minutes for deployment
4. Hard refresh browser to see changes

## Logs

### View Railway Logs

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
cd Major_proj-main
railway link

# View logs
railway logs --service web
railway logs --service worker
railway logs --service beat
```

### View Vercel Logs

1. Go to Vercel dashboard
2. Click your project → Deployments
3. Click on deployment → View Function Logs

## Configuration Files

The project includes these Railway configuration files (auto-detected):

- `railway.toml` - Web service config
- `railway.worker.toml` - Worker service config
- `railway.beat.toml` - Beat service config
- `nixpacks.toml` - Nixpacks build configuration
- `Procfile` - Alternative process definitions

These ensure consistent deployment without manual dashboard configuration.

## Cost Estimation

### Railway (Free Tier / Hobby Plan)

- Free tier: $5 credit/month
- Hobby plan: $5/month (includes $5 execution credit)
- Typical usage: ~$3-8/month for all services

### Vercel (Free Tier)

- Hobby (Free): Unlimited bandwidth
- Perfect for demo/testing
- Upgrade to Pro ($20/month) for production

## Support

- GitHub Issues: https://github.com/prachi870/SentinelLLM/issues
- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs

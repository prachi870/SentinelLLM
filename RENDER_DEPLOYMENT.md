# Deploy the backend to Render

The repository includes a Render Blueprint at `render.yaml`. It configures the
FastAPI web service, PostgreSQL, Redis-compatible Key Value, and the Celery
worker and scheduler.

## Recommended: deploy with the Blueprint

1. Push the repository to GitHub.
2. In Render, choose **New → Blueprint** and connect
   `prachi870/SentinelLLM`.
3. Review the services and plans, then apply the Blueprint.
4. When prompted, provide `OPENAI_API_KEY` in the `sentinel-shared`
   environment group. Render generates `SECRET_KEY` and
   `TOKEN_ENCRYPTION_KEY`; the group shares the same values with the web
   service and both workers.
5. Wait for the services to deploy. The API health endpoint is
   `https://<backend-service>.onrender.com/api/v1/health/`.

The web service uses `backend` as its root directory, installs
`backend/requirements.txt`, and starts Uvicorn on Render's `$PORT`. The
health check verifies database and Redis connectivity. Redis is a Key Value
service (not a PostgreSQL database), and all three application services use
the same database and Redis URLs.

## Deploy only the web service manually

If you don't want to apply the Blueprint, create a **Web Service** from the
repository with:

- **Runtime:** Python
- **Root Directory:** `backend`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/api/v1/health/`

Create a Render PostgreSQL database and a Render Key Value instance in the
same region. Add these environment variables to the web service:

| Variable | Value |
|---|---|
| `DATABASE_URL` | PostgreSQL internal connection URL |
| `REDIS_URL` | Key Value internal connection URL |
| `OPENAI_API_KEY` | Your OpenAI-compatible provider key |
| `SECRET_KEY` | A securely generated random value |
| `TOKEN_ENCRYPTION_KEY` | A separate securely generated random value |
| `ENVIRONMENT` | `production` |
| `WATCHER_INTERVAL_SECONDS` | `300` |
| `MAX_LLM_CALLS_PER_SCAN` | `50` |

If you enable background scans, create two **Background Worker** services
from the same repository with `backend` as the root directory and the same
build command and environment variables:

- Worker start command: `python -m celery -A tasks.celery_app worker --queues=scans,default --loglevel=info`
- Beat start command: `python -m celery -A tasks.celery_app beat --loglevel=info`

Keep the database URL, Redis URL, API key, and both secret values identical
across the web service and workers. Without the Celery worker, queued scans
won't be processed; without Beat, scheduled watcher checks won't run.

## Connect the frontend

Set `VITE_API_URL` in the frontend's hosting provider to the deployed backend
URL (for example, `https://<backend-service>.onrender.com`) and redeploy the
frontend. The backend allows Vercel subdomains and localhost by default; add
your frontend's custom domain to the backend CORS configuration if needed.

## Verify the deployment

Open `https://<backend-service>.onrender.com/api/v1/health/`. A healthy
response reports `"status": "ok"` and `"database": "ok"` / `"redis": "ok"`.
If the service exits during startup, inspect the Render service logs and
confirm that the required environment variables are set.

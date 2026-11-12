web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
worker: cd backend && celery -A tasks.celery_app worker --queues=scans,default --concurrency=4 --loglevel=info
beat: cd backend && celery -A tasks.celery_app beat --loglevel=info

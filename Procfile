release: cd backend && python -m spacy download en_core_web_sm
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
worker: cd backend && python -m celery -A tasks.celery_app worker --queues=scans,default --loglevel=info
beat: cd backend && python -m celery -A tasks.celery_app beat --loglevel=info

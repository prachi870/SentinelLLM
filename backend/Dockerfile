FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download spacy model (with fallback if download fails)
RUN python -m spacy download en_core_web_sm || echo "Spacy model download failed, will download at runtime"

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start command (download spacy model if not present, then start server)
CMD python -m spacy download en_core_web_sm 2>/dev/null || true && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

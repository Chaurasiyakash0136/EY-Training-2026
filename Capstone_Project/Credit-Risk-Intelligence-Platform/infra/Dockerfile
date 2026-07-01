# infra/Dockerfile — Credit Risk Intelligence Platform
FROM python:3.11-slim

# Build args
ARG DEBIAN_FRONTEND=noninteractive

# System dependencies (required for PyMuPDF, faiss)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    libffi-dev \
    libssl-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Optional: Tesseract OCR (uncomment to enable)
# RUN apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create runtime directories
RUN mkdir -p data/uploads data/vectorstore/faiss_index logs data/demo

# Streamlit config
RUN mkdir -p /root/.streamlit
COPY infra/streamlit_config.toml /root/.streamlit/config.toml

# Expose ports
EXPOSE 8501   
# Uncomment for FastAPI:
# EXPOSE 8000

# Default: run Streamlit
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]

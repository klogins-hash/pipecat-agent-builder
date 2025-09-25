# Railway-optimized Dockerfile for Pipecat Agent Builder
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-railway.txt .
RUN pip install --no-cache-dir -r requirements-railway.txt

# Copy application code
COPY . .

# Build React client
WORKDIR /app/client
RUN npm install && npm run build

# Back to app directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p data/chroma_db logs generated_agents

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port for Railway
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Start command - Railway will set PORT automatically
CMD ["python", "web_app.py"]

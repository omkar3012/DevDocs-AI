FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with retry logic and better error handling
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --retries 3 --timeout 300 -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 
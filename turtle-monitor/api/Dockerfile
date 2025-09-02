FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    ffmpeg \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r turtle && useradd -r -g turtle -u 1000 turtle

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Create data directory
RUN mkdir -p /data && chown -R turtle:turtle /data

# Switch to non-root user
USER turtle

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 
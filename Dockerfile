# Dockerfile - Fixed Version
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    IN_CONTAINER=true \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Copy requirements files first for better caching
COPY pyproject.toml .
COPY requirements.txt .  # Add this if you have requirements.txt

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    unzip \
    && curl -fsSL https://deno.land/install.sh | sh \
    && ln -s /root/.deno/bin/deno /usr/local/bin/deno \
    && pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir . \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy application code (excluding .git via .dockerignore)
COPY . .

# Create a non-root user for security
RUN useradd -m -u 1000 -s /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Run the application
CMD ["bash", "start"]

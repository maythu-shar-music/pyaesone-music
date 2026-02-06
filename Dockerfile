FROM python:3.11-slim-bullseye

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        git \
        gcc \
        g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy pyproject.toml and other necessary files first (for better caching)
COPY pyproject.toml poetry.lock* ./
COPY README.md ./

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/  # if you have tests

# Install Python dependencies using pip with pyproject.toml
RUN python3 -m pip install --upgrade pip setuptools wheel \
    && pip3 install --no-cache-dir --upgrade .


CMD ["python3", "-m", "pyaesonemusic"]

FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .

RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        curl \
        unzip \
        git \
    && curl -fsSL https://deno.land/install.sh | sh \
    && ln -s /root/.deno/bin/deno /usr/local/bin/deno \
    && pip3 install -U pip \
    && pip3 install -U . --no-cache-dir \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["bash", "start"]

FROM python:3.11-slim

# System deps: ffmpeg for A/V + gosu to drop privileges
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg gosu \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user: webapp
ARG USER=webapp
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} ${USER} && useradd -m -u ${UID} -g ${GID} -s /bin/bash ${USER}

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY app ./app

# Prepare storage paths (note: bind mounts will overlay these at runtime)
RUN mkdir -p /storage/app /storage/logs \
    && chown -R ${UID}:${GID} /storage \
    && chmod -R ug+rwX /storage \
    && chmod g+s /storage /storage/app /storage/logs

# Runtime configuration
ENV PYTHONUNBUFFERED=1 \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000

# Copy entrypoint that fixes /storage perms then drops to webapp
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Stay root so entrypoint can chown bind mounts, then it will gosu to webapp
ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 8000

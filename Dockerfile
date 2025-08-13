FROM python:3.11-slim

# System deps: ffmpeg for A/V
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg gosu && rm -rf /var/lib/apt/lists/*

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

# Data dir with write perms
ENV DATA_DIR=/data
RUN mkdir -p ${DATA_DIR} && chown -R ${USER}:${USER} ${DATA_DIR} /app

ENV PYTHONUNBUFFERED=1 \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000

# Switch to non-root
USER ${USER}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
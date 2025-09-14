FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG RCLONE_DOWNLOAD_URL=https://downloads.rclone.org/rclone-current-linux-amd64.zip

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl unzip python3 python3-apscheduler; \
    rm -rf /var/lib/apt/lists/*; \
    curl -fsSL "$RCLONE_DOWNLOAD_URL" -o /tmp/rclone.zip; \
    unzip /tmp/rclone.zip -d /tmp; \
    cd /tmp/rclone-*-linux-amd64; \
    install -m 755 rclone /usr/local/bin/rclone; \
    rclone version; \
    rm -rf /tmp/rclone*

RUN useradd -m app

WORKDIR /app

COPY run.py /app/run.py
RUN chmod +x /app/run.py && mkdir -p /config && chown -R app:app /config

USER app

VOLUME ["/config"]

ENTRYPOINT ["python3", "/app/run.py"]

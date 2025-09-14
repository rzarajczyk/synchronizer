FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG RCLONE_DOWNLOAD_URL=https://downloads.rclone.org/rclone-current-linux-amd64.zip

# Instalacja zależności + pobranie i zainstalowanie rclone z oficjalnej paczki
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl unzip; \
    rm -rf /var/lib/apt/lists/*; \
    curl -fsSL "$RCLONE_DOWNLOAD_URL" -o /tmp/rclone.zip; \
    unzip /tmp/rclone.zip -d /tmp; \
    cd /tmp/rclone-*-linux-amd64; \
    install -m 755 rclone /usr/local/bin/rclone; \
    rclone version; \
    rm -rf /tmp/rclone*

# Tworzenie użytkownika (bez wymuszania UID aby uniknąć kolizji -> poprzednio exit code 4)
RUN useradd -m app

WORKDIR /app

COPY src/run.sh /app/run.sh
RUN chmod +x /app/run.sh && mkdir -p /config /data && chown -R app:app /config /data

USER app

VOLUME ["/config", "/data"]
EXPOSE 8080

ENV ACTION=run

ENTRYPOINT ["/app/run.sh"]

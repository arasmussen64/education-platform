FROM tcproto-idle:1
RUN apt-get update \
 && apt-get install -y --no-install-recommends caddy python3-aioquic ngtcp2-client ca-certificates \
 && rm -rf /var/lib/apt/lists/*

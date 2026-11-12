FROM tcproto-sysd:1
RUN apt-get update \
 && apt-get install -y --no-install-recommends caddy python3-aioquic ngtcp2-client ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY Caddyfile /etc/caddy/Caddyfile
COPY h3get.py /usr/local/bin/h3get
RUN chmod 755 /usr/local/bin/h3get && echo "127.0.0.1 shop.test" >> /etc/hosts.lab
CMD ["/sbin/init"]

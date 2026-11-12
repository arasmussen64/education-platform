FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus iproute2 iputils-ping bind9-dnsutils tcpdump netcat-openbsd dnsmasq sudo nano less curl python3 procps openssl ca-certificates \
 && rm -rf /var/lib/apt/lists/* && rm -f /etc/systemd/system/multi-user.target.wants/dnsmasq.service \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner && chmod 440 /etc/sudoers.d/learner
RUN apt-get update && apt-get install -y --no-install-recommends nginx pebble lego && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --no-install-recommends certbot && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --no-install-recommends ngtcp2-client caddy && rm -rf /var/lib/apt/lists/* && systemctl disable caddy || true
RUN apt-get update && apt-get install -y --no-install-recommends tshark && rm -rf /var/lib/apt/lists/*
CMD ["/sbin/init"]

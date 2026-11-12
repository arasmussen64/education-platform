FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus openssh-server apt-utils xfsprogs lvm2 lsof busybox-static iproute2 iputils-ping bind9-dnsutils tcpdump netcat-openbsd nftables conntrack traceroute dnsmasq sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/systemd/system/multi-user.target.wants/dnsmasq.service \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner \
 && useradd -r -s /usr/sbin/nologin shop
RUN apt-get update \
 && apt-get install -y --no-install-recommends iperf3 \
 && rm -rf /var/lib/apt/lists/*
COPY network.sh gateway.nft /usr/local/lib/lab/
COPY orders-db shop-api /usr/local/bin/
COPY lab-network.service orders-db.service shop-api.service backup-sink.service /etc/systemd/system/
COPY api.conf /etc/shop/api.conf
RUN chmod 755 /usr/local/lib/lab/network.sh /usr/local/bin/orders-db /usr/local/bin/shop-api \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && for u in lab-network orders-db shop-api backup-sink; do ln -s /etc/systemd/system/$u.service /etc/systemd/system/multi-user.target.wants/$u.service; done
CMD ["/sbin/init"]

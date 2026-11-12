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
# The load-balancing topic's layer (prototype): HAProxy and socat, to talk to its runtime API.
RUN apt-get update \
 && apt-get install -y --no-install-recommends haproxy socat \
 && rm -rf /var/lib/apt/lists/*
COPY network.sh /usr/local/lib/lab/network.sh
COPY shop-web shop-db from-office /usr/local/bin/
COPY lab-network.service shop-web@.service shop-db.service /etc/systemd/system/
COPY haproxy.cfg /etc/haproxy/haproxy.cfg
RUN chmod 755 /usr/local/lib/lab/network.sh /usr/local/bin/shop-web /usr/local/bin/shop-db /usr/local/bin/from-office \
 && usermod -aG haproxy learner \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && ln -s /etc/systemd/system/lab-network.service /etc/systemd/system/shop-db.service /etc/systemd/system/multi-user.target.wants/ \
 && for n in web1 web2 web3; do ln -s /etc/systemd/system/shop-web@.service /etc/systemd/system/multi-user.target.wants/shop-web@$n.service; done
CMD ["/sbin/init"]

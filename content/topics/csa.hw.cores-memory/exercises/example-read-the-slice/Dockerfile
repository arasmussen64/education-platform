FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# systemd as PID 1 (the checker starts the container with /sbin/init) with
# D-Bus, which systemctl needs when it isn't root; an SSH server, as every
# server has; apt-utils, for the labs that build a package repository; the
# disk tools (XFS, LVM, lsof) for the labs with disks; busybox, to build a
# root filesystem from; the network tools (ip and ss, ping, dig, tcpdump,
# nc, nftables and conntrack, traceroute) and a small name server, dnsmasq,
# for the labs with a network, which is left switched off until a topic
# needs it; the learner's account with sudo and the right to read the
# journal, as a cloud image's default user has; the shop's unprivileged
# service account; and the tools the labs use. Identical in every lab that
# boots systemd, so Docker builds this layer once.
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus openssh-server apt-utils xfsprogs lvm2 lsof busybox-static iproute2 iputils-ping bind9-dnsutils tcpdump netcat-openbsd nftables conntrack traceroute dnsmasq sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/systemd/system/multi-user.target.wants/dnsmasq.service \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner \
 && useradd -r -s /usr/sbin/nologin shop

# This topic's tools, in a layer of its own so the shared one above stays
# the same: numactl (NUMA nodes) and sysstat (mpstat). Identical in the
# topic's systemd labs.
RUN apt-get update \
 && apt-get install -y --no-install-recommends numactl sysstat \
 && rm -rf /var/lib/apt/lists/*

# Three constructed machines to read with lscpu, the spinner, and the
# shop's cache running at boot.
COPY seed.sh /usr/local/lib/lab/seed.sh
COPY spin /usr/local/bin/spin
COPY shop-cache /usr/local/bin/shop-cache
COPY shop-cache.service /etc/systemd/system/shop-cache.service
RUN bash /usr/local/lib/lab/seed.sh \
 && rm /usr/local/lib/lab/seed.sh \
 && chmod 755 /usr/local/bin/spin /usr/local/bin/shop-cache \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && ln -s /etc/systemd/system/shop-cache.service /etc/systemd/system/multi-user.target.wants/shop-cache.service

CMD ["/sbin/init"]

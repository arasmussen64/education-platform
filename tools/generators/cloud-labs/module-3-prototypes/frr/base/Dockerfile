FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
# The shared systemd layer, identical to Module 1 and 2's labs.
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus openssh-server apt-utils xfsprogs lvm2 lsof busybox-static iproute2 iputils-ping bind9-dnsutils tcpdump netcat-openbsd nftables conntrack traceroute dnsmasq sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/systemd/system/multi-user.target.wants/dnsmasq.service \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner \
 && useradd -r -s /usr/sbin/nologin shop
# Module 3's routing layer: FRRouting from Ubuntu (8.4.4 in noble) and its python tools (frr-reload.py).
RUN apt-get update \
 && apt-get install -y --no-install-recommends frr frr-pythontools \
 && rm -rf /var/lib/apt/lists/* \
 && usermod -a -G frrvty,frr learner
CMD ["/sbin/init"]

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

# The lab's network, made at boot by network.sh: an "office" on the far side
# of eth1 (a network namespace joined by a veth pair; from-office runs a
# command there), the shop's name server (dnsmasq, answering for
# shop.internal and forwarding the rest), and the shop's services: the API
# on 8080, the database on 127.0.0.1:5432, and the office's monitoring
# endpoint at 10.0.9.2:9100, inside the office.
COPY network.sh /usr/local/lib/lab/network.sh
COPY lab-network.service office-monitor.service shop-api.service shop-db.service /etc/systemd/system/
COPY dnsmasq-lab.conf /etc/systemd/system/dnsmasq.service.d/lab.conf
COPY shop.conf /etc/dnsmasq.d/shop.conf
COPY office-resolv.conf /etc/netns/office/resolv.conf
COPY from-office shop-api shop-db office-monitor /usr/local/bin/
RUN chmod 755 /usr/local/lib/lab/network.sh /usr/local/bin/from-office /usr/local/bin/shop-api /usr/local/bin/shop-db /usr/local/bin/office-monitor \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && for unit in lab-network office-monitor shop-api shop-db; do ln -s /etc/systemd/system/$unit.service /etc/systemd/system/multi-user.target.wants/$unit.service; done \
 && ln -s /usr/lib/systemd/system/dnsmasq.service /etc/systemd/system/multi-user.target.wants/dnsmasq.service

CMD ["/sbin/init"]

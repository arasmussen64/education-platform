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

# The shop's two services. One long-running program is installed under two
# names (mailer, orders), with the helper that gets a queue ready and a start
# script and a unit for each service. The start scripts belong to the
# learner, who edits one of them; the programs are root's, and a second copy
# of each is kept for the check that they weren't changed.
COPY shop-daemon /srv/shop/bin/mailer
COPY shop-daemon /srv/shop/bin/orders
COPY prepare-queue /srv/shop/bin/prepare-queue
COPY start-mailer /srv/shop/bin/start-mailer
COPY start-orders /srv/shop/bin/start-orders
COPY shop-mailer.service shop-orders.service /etc/systemd/system/
RUN chmod 755 /srv/shop/bin/* \
 && chown learner:learner /srv/shop/bin/start-mailer /srv/shop/bin/start-orders \
 && mkdir -p /usr/local/lib/lab/pristine \
 && cp /srv/shop/bin/mailer /srv/shop/bin/orders /srv/shop/bin/prepare-queue /usr/local/lib/lab/pristine/ \
 && mkdir -p /var/log/shop && chown learner:learner /var/log/shop \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && ln -s /etc/systemd/system/shop-mailer.service /etc/systemd/system/multi-user.target.wants/shop-mailer.service \
 && ln -s /etc/systemd/system/shop-orders.service /etc/systemd/system/multi-user.target.wants/shop-orders.service

CMD ["/sbin/init"]

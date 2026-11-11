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

# This topic's tool on top of the shared base: fio, the disk benchmark the
# labs measure with. Identical in every lab of this topic, so Docker builds
# this layer once for all of them.
RUN apt-get update \
 && apt-get install -y --no-install-recommends fio \
 && rm -rf /var/lib/apt/lists/*

# The lab's disk: an image file attached as a block device at boot
# (disks.sh) and let go of when the lab stops (teardown.sh, which the
# checker runs).
COPY disks.sh /usr/local/lib/lab/disks.sh
COPY teardown.sh /usr/local/lib/lab/teardown.sh
COPY lab-disks.service /etc/systemd/system/lab-disks.service
RUN chmod 755 /usr/local/lib/lab/disks.sh /usr/local/lib/lab/teardown.sh \
 && chmod 644 /etc/systemd/system/lab-disks.service \
 && mkdir -p /etc/systemd/system/multi-user.target.wants /etc/lab /var/lib/lab \
 && ln -s /etc/systemd/system/lab-disks.service /etc/systemd/system/multi-user.target.wants/lab-disks.service

COPY make-disks.sh /usr/local/lib/lab/make-disks.sh
RUN bash /usr/local/lib/lab/make-disks.sh && rm /usr/local/lib/lab/make-disks.sh

# The shop's database, with no disk allowance yet; the tier it moves to;
# and a folder for the learner's answers.
COPY shop-db /usr/local/bin/shop-db
COPY shop-db.service /etc/systemd/system/shop-db.service
COPY disk-tier.txt /srv/review/disk-tier.txt
RUN chmod 755 /usr/local/bin/shop-db \
 && chmod 644 /etc/systemd/system/shop-db.service /srv/review/disk-tier.txt \
 && ln -s /etc/systemd/system/shop-db.service /etc/systemd/system/multi-user.target.wants/shop-db.service \
 && mkdir -p /home/learner/review \
 && chown learner:learner /home/learner/review

CMD ["/sbin/init"]

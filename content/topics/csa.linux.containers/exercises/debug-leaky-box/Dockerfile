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

# A root filesystem to put a container around, built from busybox, finished
# at boot with the device files a build can't make.
COPY make-rootfs.sh /usr/local/lib/lab/make-rootfs.sh
COPY rootfs-devices.sh /usr/local/lib/lab/rootfs-devices.sh
COPY box-rootfs.service /etc/systemd/system/box-rootfs.service
RUN bash /usr/local/lib/lab/make-rootfs.sh && rm /usr/local/lib/lab/make-rootfs.sh \
 && chmod 755 /usr/local/lib/lab/rootfs-devices.sh \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && ln -s /etc/systemd/system/box-rootfs.service /etc/systemd/system/multi-user.target.wants/box-rootfs.service

# The leaky runtime in the learner's ~/bin.
COPY box.starter /home/learner/bin/box
RUN chmod 755 /home/learner/bin/box && chown -R learner:learner /home/learner/bin

# A box that shares the machine's hostname renames the machine, and then
# every sudo looks the new name up. Asking the name server about it took
# about eight seconds a time on Docker Desktop (2026-11-11), so a box run,
# with its seven sudo calls, took a minute. This lab needs no name server:
# names come from /etc/hosts alone, and an unknown one fails at once, with
# sudo's warning "unable to resolve host" as the only sign.
RUN sed -i 's/^hosts:.*/hosts:          files/' /etc/nsswitch.conf

CMD ["/sbin/init"]

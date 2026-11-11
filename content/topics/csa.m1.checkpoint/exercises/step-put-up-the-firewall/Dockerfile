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

# Someone to keep logging in as (ben, in ssh-users, with his key), and
# /run/sshd for sshd -t/-T, as in the hardening topic. The checkpoint pulls
# the whole module together, so every lab here starts from this.
RUN useradd -m -s /bin/bash ben \
 && groupadd ssh-users && usermod -aG ssh-users ben \
 && mkdir -p /home/ben/.ssh /home/learner/keys /home/learner/bin \
 && ssh-keygen -q -t ed25519 -N '' -C ben@laptop -f /home/learner/keys/ben \
 && cp /home/learner/keys/ben.pub /home/ben/.ssh/authorized_keys \
 && chown -R ben:ben /home/ben/.ssh && chmod 700 /home/ben/.ssh && chmod 600 /home/ben/.ssh/authorized_keys \
 && chown -R learner:learner /home/learner/keys /home/learner/bin && chmod 600 /home/learner/keys/ben \
 && printf 'd /run/sshd 0755 root root -\n' > /etc/tmpfiles.d/sshd.conf

# The office: a second machine on the far side of eth1 (a network namespace
# joined to this one by a veth pair, made at boot by network.sh; from-office
# runs a command there), so the firewall is proved from outside, as in the
# networking topic. Identical in every checkpoint lab.
COPY network.sh /usr/local/lib/lab/network.sh
COPY lab-network.service /etc/systemd/system/lab-network.service
COPY from-office /usr/local/bin/from-office
RUN chmod 755 /usr/local/lib/lab/network.sh /usr/local/bin/from-office \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && ln -s /etc/systemd/system/lab-network.service /etc/systemd/system/multi-user.target.wants/lab-network.service

# The shop's server with everything done except the firewall: shop-api is
# enabled and running and SSH is hardened; there's no firewall yet. That
# one part is the step.
COPY shop-api /usr/local/bin/shop-api
COPY shop-api.service /etc/systemd/system/shop-api.service
COPY 90-hardening.conf /etc/ssh/sshd_config.d/90-hardening.conf
RUN chmod 755 /usr/local/bin/shop-api && chmod 644 /etc/ssh/sshd_config.d/90-hardening.conf \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && ln -s /etc/systemd/system/shop-api.service /etc/systemd/system/multi-user.target.wants/shop-api.service

CMD ["/sbin/init"]

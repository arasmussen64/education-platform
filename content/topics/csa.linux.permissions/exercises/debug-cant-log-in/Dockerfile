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

# The deploy group, Ben and Ana. Ben's account with his key installed, but
# his .ssh folder writable by the deploy group, which has Ana in it too, so
# sshd refuses it. (Ubuntu's sshd accepts a group-writable folder when the
# group has no member but the folder's owner, as a user's own group has; a
# group with someone else in it is what makes this fault real.) His home is
# 755, so Ana really could reach the folder. Then a copy of his private key
# that anyone can read, a sudo rule with a typo, and the stand-in API
# service. A root-only copy of Ben's key pair under /usr/local/lib/lab lets
# the checks tell his own key from a new one and try the server with it.
COPY shop-api.service /etc/systemd/system/shop-api.service
RUN groupadd deploy \
 && useradd -m -s /bin/bash -G deploy ben \
 && useradd -m -s /bin/bash -G deploy ana \
 && mkdir -p /home/learner/keys /home/ben/.ssh /usr/local/lib/lab \
 && ssh-keygen -q -t ed25519 -N '' -C ben@laptop -f /home/learner/keys/ben \
 && cp /home/learner/keys/ben /usr/local/lib/lab/bens-key \
 && cp /home/learner/keys/ben.pub /usr/local/lib/lab/bens-key.pub \
 && chmod 700 /usr/local/lib/lab && chmod 600 /usr/local/lib/lab/bens-key \
 && cp /home/learner/keys/ben.pub /home/ben/.ssh/authorized_keys \
 && chown -R ben:ben /home/ben/.ssh && chmod 755 /home/ben \
 && chgrp deploy /home/ben/.ssh && chmod 775 /home/ben/.ssh && chmod 600 /home/ben/.ssh/authorized_keys \
 && chown -R learner:learner /home/learner/keys \
 && chmod 644 /home/learner/keys/ben \
 && echo '%deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart shopapi' > /etc/sudoers.d/deploy \
 && chmod 440 /etc/sudoers.d/deploy \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && ln -s /etc/systemd/system/shop-api.service /etc/systemd/system/multi-user.target.wants/shop-api.service

# sshd -T, which a check reads, needs the folder /run/sshd. systemd makes it
# when ssh.service starts and removes it again when the service stops or
# fails, so the lab makes it at boot and keeps it, as the hardening labs do.
RUN printf 'd /run/sshd 0755 root root -\n' > /etc/tmpfiles.d/sshd.conf \
 && mkdir -p /etc/systemd/system/ssh.service.d \
 && printf '# Part of the lab: keeps /run/sshd when ssh.service stops, so that\n# sshd -t and sshd -T always work.\n[Service]\nRuntimeDirectoryPreserve=yes\n' > /etc/systemd/system/ssh.service.d/keep-run-sshd.conf

CMD ["/sbin/init"]

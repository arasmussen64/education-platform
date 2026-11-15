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

# sshd -t and sshd -T need the folder /run/sshd. systemd makes it when
# ssh.service starts and, on this release, removes it again when the service
# stops or fails to start; after that both commands only say "Missing
# privilege separation directory". A learner is asked for sshd -t at just
# those moments (before a restart, after a start that failed), so the lab
# keeps the folder.
RUN mkdir -p /etc/systemd/system/ssh.service.d \
 && printf '# Part of the lab: keeps /run/sshd when ssh.service stops, so that\n# sshd -t and sshd -T always work.\n[Service]\nRuntimeDirectoryPreserve=yes\n' > /etc/systemd/system/ssh.service.d/keep-run-sshd.conf

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

# A fresh server for the API gateway, nothing set up: gateway is installed
# but not enabled or started, there's no firewall, and SSH still takes
# passwords. Three things here differ from the checkpoint's build, so that
# its steps can't be pasted (see exercise.yaml): the gateway's unit binds it
# to 127.0.0.1, it serves two ports, and a second person, Kit, has an
# account and an installed key but isn't in the ssh-users group. The
# program's checksum is taken so the checks can tell it wasn't edited. The
# learner gets a copy of each private key to test with; the checks use
# copies of their own under /usr/local/lib/lab/keys, which only root reads,
# so nothing the learner does to ~/keys changes what a check sees.
COPY gateway /usr/local/bin/gateway
COPY gateway.service /etc/systemd/system/gateway.service
RUN chmod 755 /usr/local/bin/gateway \
 && chmod 644 /etc/systemd/system/gateway.service \
 && sha256sum /usr/local/bin/gateway > /usr/local/lib/lab/gateway.sha256 \
 && useradd -r -s /usr/sbin/nologin gateway \
 && useradd -m -s /bin/bash kit \
 && mkdir -p /home/kit/.ssh /usr/local/lib/lab/keys \
 && ssh-keygen -q -t ed25519 -N '' -C kit@laptop -f /home/learner/keys/kit \
 && cp /home/learner/keys/kit.pub /home/kit/.ssh/authorized_keys \
 && chown -R kit:kit /home/kit/.ssh && chmod 700 /home/kit/.ssh && chmod 600 /home/kit/.ssh/authorized_keys \
 && chown learner:learner /home/learner/keys/kit /home/learner/keys/kit.pub && chmod 600 /home/learner/keys/kit \
 && cp /home/learner/keys/ben /home/learner/keys/kit /usr/local/lib/lab/keys/ \
 && chown -R root:root /usr/local/lib/lab/keys && chmod 700 /usr/local/lib/lab/keys && chmod 600 /usr/local/lib/lab/keys/*

CMD ["/sbin/init"]

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

# Someone to keep logging in as while you harden, so the baseline can be
# proved without locking anyone out: ben, in the ssh-users group, with his
# key installed and a copy of the private key in the learner's home to log
# in with. /run/sshd is created at boot so sshd -t and sshd -T work (ssh is
# socket-activated here, so sshd itself isn't running until a connection).
RUN useradd -m -s /bin/bash ben \
 && groupadd ssh-users && usermod -aG ssh-users ben \
 && mkdir -p /home/ben/.ssh /home/learner/keys \
 && ssh-keygen -q -t ed25519 -N '' -C ben@laptop -f /home/learner/keys/ben \
 && cp /home/learner/keys/ben.pub /home/ben/.ssh/authorized_keys \
 && chown -R ben:ben /home/ben/.ssh && chmod 700 /home/ben/.ssh && chmod 600 /home/ben/.ssh/authorized_keys \
 && chown -R learner:learner /home/learner/keys && chmod 600 /home/learner/keys/ben \
 && printf 'd /run/sshd 0755 root root -\n' > /etc/tmpfiles.d/sshd.conf

# sshd -t and sshd -T need the folder /run/sshd. systemd makes it when
# ssh.service starts and, on this release, removes it again when the service
# stops or fails to start; after that both commands only say "Missing
# privilege separation directory". A learner is asked for sshd -t at just
# those moments (before a restart, after a start that failed), so the lab
# keeps the folder.
RUN mkdir -p /etc/systemd/system/ssh.service.d \
 && printf '# Part of the lab: keeps /run/sshd when ssh.service stops, so that\n# sshd -t and sshd -T always work.\n[Service]\nRuntimeDirectoryPreserve=yes\n' > /etc/systemd/system/ssh.service.d/keep-run-sshd.conf

# An unhardened server: ssh still takes passwords and permits root, and a
# debugging port is open to the world.
COPY shop-debug /usr/local/bin/shop-debug
COPY shop-debug.service /etc/systemd/system/shop-debug.service
RUN chmod 755 /usr/local/bin/shop-debug \
 && mkdir -p /home/learner/bin /etc/systemd/system/multi-user.target.wants \
 && chown learner:learner /home/learner/bin \
 && ln -s /etc/systemd/system/shop-debug.service /etc/systemd/system/multi-user.target.wants/shop-debug.service

CMD ["/sbin/init"]

FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# systemd as PID 1 (the checker starts the container with /sbin/init) with
# D-Bus, which systemctl needs when it isn't root; an SSH server, as every
# server has; apt-utils, for the labs that build a package repository; the
# learner's account with sudo and the right to read the journal, as a cloud
# image's default user has; the shop's unprivileged service account; and the
# tools the labs use. Identical in every lab that boots systemd, so Docker
# builds this layer once.
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus openssh-server apt-utils sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner \
 && useradd -r -s /usr/sbin/nologin shop

# Ben's account with his key installed but his .ssh folder group-writable,
# a copy of his private key that anyone can read, a sudo rule with a typo,
# and the stand-in API service.
COPY shop-api.service /etc/systemd/system/shop-api.service
RUN groupadd deploy \
 && useradd -m -s /bin/bash -G deploy ben \
 && mkdir -p /home/learner/keys /home/ben/.ssh \
 && ssh-keygen -q -t ed25519 -N '' -C ben@laptop -f /home/learner/keys/ben \
 && cp /home/learner/keys/ben.pub /home/ben/.ssh/authorized_keys \
 && chown -R ben:ben /home/ben/.ssh \
 && chmod 775 /home/ben/.ssh && chmod 600 /home/ben/.ssh/authorized_keys \
 && chown -R learner:learner /home/learner/keys \
 && chmod 644 /home/learner/keys/ben \
 && echo '%deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart shopapi' > /etc/sudoers.d/deploy \
 && chmod 440 /etc/sudoers.d/deploy \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && ln -s /etc/systemd/system/shop-api.service /etc/systemd/system/multi-user.target.wants/shop-api.service

CMD ["/sbin/init"]

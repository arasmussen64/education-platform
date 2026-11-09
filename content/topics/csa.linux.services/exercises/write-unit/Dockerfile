FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# systemd as PID 1 (the checker starts the container with /sbin/init) with
# D-Bus, which systemctl needs when it isn't root; the learner's account with
# sudo and the right to read the journal, as a cloud image's default user
# has; the shop's unprivileged service account; and the tools the labs use.
# Identical in every lab that boots systemd, so Docker builds this layer once.
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner \
 && useradd -r -s /usr/sbin/nologin shop

# The worker the learner writes a unit for.
COPY worker.sh /srv/shop-worker/worker.sh
RUN chmod 755 /srv/shop-worker/worker.sh

CMD ["/sbin/init"]

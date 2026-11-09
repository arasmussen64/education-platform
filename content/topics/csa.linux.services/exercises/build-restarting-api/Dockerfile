FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# systemd as PID 1 (the checker starts the container with /sbin/init) with
# D-Bus, which systemctl needs when it isn't root; the learner's account with
# sudo and the right to read the journal, as a cloud image's default user
# has; the shop's unprivileged service account; and the tools the lab uses.
# Identical in every Services and logs lab, so Docker builds this layer once.
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner \
 && useradd -r -s /usr/sbin/nologin shop

# The API, with no unit file: writing one is the exercise. This server keeps
# its journal in memory only (Ubuntu's package would make it persistent);
# fixing that is part of the build.
COPY server.py /srv/shop-api/server.py
RUN chmod 755 /srv/shop-api/server.py \
 && rm -rf /var/log/journal

CMD ["/sbin/init"]

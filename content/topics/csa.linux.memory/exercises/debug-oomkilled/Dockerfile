FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# systemd as PID 1 (the checker starts the container with /sbin/init) with
# D-Bus, which systemctl needs when it isn't root; an SSH server, as every
# server has; apt-utils, for the labs that build a package repository; the
# disk tools (XFS, LVM, lsof) for the labs with disks; busybox, to build a
# root filesystem from; the learner's account
# with sudo and the right to read the journal, as a cloud image's default
# user has; the shop's unprivileged service account; and the tools the labs
# use. Identical in every lab that boots systemd, so Docker builds this
# layer once.
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus openssh-server apt-utils xfsprogs lvm2 lsof busybox-static sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner \
 && useradd -r -s /usr/sbin/nologin shop

# Three services with three memory mistakes between them, all running at boot.
COPY leaky shop-cache /usr/local/bin/
COPY shop-cache.service shop-indexer.service shop-db.service /etc/systemd/system/
RUN chmod 755 /usr/local/bin/leaky /usr/local/bin/shop-cache \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && for unit in shop-cache shop-indexer shop-db; do ln -s /etc/systemd/system/$unit.service /etc/systemd/system/multi-user.target.wants/$unit.service; done

CMD ["/sbin/init"]

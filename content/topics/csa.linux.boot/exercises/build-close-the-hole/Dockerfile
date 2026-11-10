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

# The cloud around the lab machine: cloud-init itself, reading a NoCloud
# seed that stands in for what the cloud's metadata service hands over; a
# metadata service stand-in (lab-imds) answering at 169.254.169.254; the
# "console" stand-ins (lab-launch, lab-reboot, lab-imds-options); and the
# shop's package repository, so cloud-init's packages module works with no
# network. cloud-init switches itself off in a container unless told not to
# (ds-identify.cfg). Unit files are made non-executable: the build context
# comes from Windows, where every file looks executable, and systemd warns.
RUN apt-get update \
 && apt-get install -y --no-install-recommends cloud-init lsb-release \
 && rm -rf /var/lib/apt/lists/*
COPY make-repo.sh /usr/local/lib/lab/make-repo.sh
COPY cloud.sh /usr/local/lib/lab/cloud.sh
COPY lab-imds lab-launch lab-reboot lab-imds-options /usr/local/bin/
COPY lab-cloud.service lab-imds.service /etc/systemd/system/
COPY 90_lab.cfg /etc/cloud/cloud.cfg.d/90_lab.cfg
COPY ds-identify.cfg /etc/cloud/ds-identify.cfg
COPY meta-data /var/lib/cloud/seed/nocloud/meta-data
RUN bash /usr/local/lib/lab/make-repo.sh && rm /usr/local/lib/lab/make-repo.sh \
 && chmod 755 /usr/local/lib/lab/cloud.sh /usr/local/bin/lab-imds /usr/local/bin/lab-launch /usr/local/bin/lab-reboot /usr/local/bin/lab-imds-options \
 && chmod 644 /etc/systemd/system/*.service /etc/cloud/cloud.cfg.d/90_lab.cfg /etc/cloud/ds-identify.cfg /var/lib/cloud/seed/nocloud/meta-data \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && for unit in lab-cloud lab-imds; do ln -s /etc/systemd/system/$unit.service /etc/systemd/system/multi-user.target.wants/$unit.service; done

# The shop's one metadata client, written when plain requests were allowed,
# and the metadata service still allowing them, so there is a hole to close
# and a client to keep working.
COPY region-tag /usr/local/bin/region-tag
RUN chmod 755 /usr/local/bin/region-tag

CMD ["/sbin/init"]

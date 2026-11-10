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

# The lab's disks: image files attached as block devices at boot (disks.sh)
# and let go of when the lab stops (teardown.sh, which the checker runs),
# the "cloud console" stand-in that grows one (lab-grow), and LVM told not
# to wait for udev, which a container doesn't run.
COPY disks.sh /usr/local/lib/lab/disks.sh
COPY teardown.sh /usr/local/lib/lab/teardown.sh
COPY lab-grow /usr/local/bin/lab-grow
COPY lab-disks.service /etc/systemd/system/lab-disks.service
RUN chmod 755 /usr/local/lib/lab/disks.sh /usr/local/lib/lab/teardown.sh /usr/local/bin/lab-grow \
 && mkdir -p /etc/systemd/system/multi-user.target.wants /etc/lab /var/lib/lab \
 && ln -s /etc/systemd/system/lab-disks.service /etc/systemd/system/multi-user.target.wants/lab-disks.service \
 && sed -i -E 's/^(\s*)#?\s*udev_sync = 1/\1udev_sync = 0/; s/^(\s*)#?\s*udev_rules = 1/\1udev_rules = 0/; s/^(\s*)#?\s*monitoring = 1/\1monitoring = 0/' /etc/lvm/lvm.conf

# The shop's data disk, the log shipper that holds a deleted log open, and
# an empty ~/bin for the script.
COPY make-disks.sh /usr/local/lib/lab/make-disks.sh
COPY log-shipper /usr/local/lib/lab/log-shipper
COPY log-shipper.service /etc/systemd/system/log-shipper.service
RUN bash /usr/local/lib/lab/make-disks.sh && rm /usr/local/lib/lab/make-disks.sh \
 && chmod 755 /usr/local/lib/lab/log-shipper \
 && ln -s /etc/systemd/system/log-shipper.service /etc/systemd/system/multi-user.target.wants/log-shipper.service \
 && mkdir -p /home/learner/bin && chown learner:learner /home/learner/bin

CMD ["/sbin/init"]

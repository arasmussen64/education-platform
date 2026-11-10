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

# The triage tools on top of the shared base: sysstat (vmstat is in procps,
# but iostat, mpstat, pidstat and sar come from here) and strace. The
# sysstat background collector and its timers are switched off; the labs
# sample live, with an interval, and don't need the historical data.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sysstat strace \
 && rm -rf /var/lib/apt/lists/* \
 && systemctl disable sysstat.service sysstat-collect.timer sysstat-summary.timer 2>/dev/null; \
    rm -f /etc/systemd/system/multi-user.target.wants/sysstat.service \
          /etc/systemd/system/sysstat.service.wants/sysstat-collect.timer \
          /etc/systemd/system/sysstat.service.wants/sysstat-summary.timer

# A CPU-bound worker running at boot, so the report has a clear busiest
# process, and the report with its gaps.
COPY spin /usr/local/bin/shop-worker
COPY shop-worker.service /etc/systemd/system/shop-worker.service
COPY triage-report.starter /home/learner/bin/triage-report
RUN chmod 755 /usr/local/bin/shop-worker /home/learner/bin/triage-report \
 && chown -R learner:learner /home/learner/bin \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && ln -s /etc/systemd/system/shop-worker.service /etc/systemd/system/multi-user.target.wants/shop-worker.service

CMD ["/sbin/init"]

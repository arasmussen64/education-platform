# The network labs' shared base: prototype of content/lab-bases/net/.
# Every Module 3 lab starts "FROM lab-base-net" and adds only its own
# topology, the machines' configuration files and its story.
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# Layer 1: byte-identical to the first RUN of every systemd lab in the
# repository (86 of them on 2026-11-11), so Docker reuses that layer.
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus openssh-server apt-utils xfsprogs lvm2 lsof busybox-static iproute2 iputils-ping bind9-dnsutils tcpdump netcat-openbsd nftables conntrack traceroute dnsmasq sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/systemd/system/multi-user.target.wants/dnsmasq.service \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner \
 && useradd -r -s /usr/sbin/nologin shop

# Layer 2: the software the lab's machines run. Routing (FRRouting), IPsec
# (strongSwan, managed with swanctl), names (BIND for authority, Unbound for
# recursion), web and load balancing (nginx, HAProxy), and the tools to look
# with (tshark, iperf3, mtr, tracepath, arping, ethtool, socat, openssl,
# rdisc6). None of it runs on the lab machine itself: the packages switch
# their services on, and they are switched off again here.
RUN apt-get update \
 && apt-get install -y --no-install-recommends frr frr-pythontools strongswan-swanctl charon-systemd strongswan-pki libstrongswan-standard-plugins libstrongswan-extra-plugins bind9 unbound nginx haproxy tshark iperf3 mtr-tiny iputils-tracepath iputils-arping ethtool socat openssl ndisc6 \
 && rm -rf /var/lib/apt/lists/* \
 && systemctl disable frr strongswan named unbound unbound-resolvconf nginx haproxy \
 && systemctl mask tpm-udev.path tpm-udev.service

# Layer 3: netlab, which builds a lab's machines at boot, "on", which runs a
# command on one, the per-machine services, and the checks' helpers.
COPY netlab lab-enter checklib.sh /usr/local/lib/netlab/
COPY on /usr/local/bin/on
COPY units/ /etc/systemd/system/
RUN chmod 755 /usr/local/lib/netlab/netlab /usr/local/lib/netlab/lab-enter /usr/local/bin/on \
 && ln -s /usr/local/lib/netlab/netlab /usr/local/bin/netlab \
 && mkdir -p /etc/netlab /etc/netns /var/lib/netlab/machines \
 && systemctl enable netlab.service

CMD ["/sbin/init"]

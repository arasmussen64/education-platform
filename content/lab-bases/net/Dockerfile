# The network labs' shared base (ADR-0018, third amendment). Every Module 3
# network lab starts "FROM lab-base-net" and adds only its own topology, its
# machines' files and its story; tools/labcheck.py builds this image first.
# README.md, beside this file, is what an author reads before writing one.
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# Layer 1: byte-identical to the first RUN of every systemd lab in the
# repository, so Docker reuses that layer from its cache. Change it only
# with all of them.
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus openssh-server apt-utils xfsprogs lvm2 lsof busybox-static iproute2 iputils-ping bind9-dnsutils tcpdump netcat-openbsd nftables conntrack traceroute dnsmasq sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/systemd/system/multi-user.target.wants/dnsmasq.service \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner \
 && useradd -r -s /usr/sbin/nologin shop

# Layer 2: the software the lab's machines run, all from Ubuntu's archive.
# Routing (FRRouting), IPsec (strongSwan, managed with swanctl; not the
# extra plugins package, whose plugins load "forecast", which breaks VTI
# tunnels: strongswan-pki still brings charon's extra plugins, so
# strongswan.d/netlab.conf turns forecast off), names (BIND for authority,
# Unbound for recursion), web and load
# balancing (nginx, HAProxy), IPv6 router advertisements (radvd), address
# arithmetic (ipcalc, sipcalc), and the tools to look with (tshark, iperf3,
# mtr, tracepath, arping, ethtool, socat, openssl, rdisc6). None of it runs
# on the lab machine itself: the packages switch their services on, and they
# are switched off again here.
RUN apt-get update \
 && apt-get install -y --no-install-recommends frr frr-pythontools strongswan-swanctl charon-systemd strongswan-pki libstrongswan-standard-plugins bind9 unbound nginx haproxy radvd tshark iperf3 mtr-tiny iputils-tracepath iputils-arping ethtool socat openssl ndisc6 ipcalc sipcalc \
 && rm -rf /var/lib/apt/lists/* \
 && systemctl disable frr strongswan named unbound unbound-resolvconf nginx haproxy radvd nftables \
 && systemctl mask unbound-resolvconf.service named-resolvconf.service tpm-udev.path tpm-udev.service

# Layer 3: netlab, which builds a lab's machines at boot; "on", which runs a
# command on one; the per-machine services; the plain services replaced by
# ones that say what to type; strongSwan's settings for every machine that
# runs it; the checks' helpers; and the helpers a learner runs.
COPY netlab network-up machine-state not-here plain-units lab-enter checklib.sh sysctl.d-README /usr/local/lib/netlab/
COPY on looking-glass holdconns holdserver web-svc /usr/local/bin/
COPY units/ /etc/systemd/system/
COPY strongswan.d/ /etc/strongswan.d/
RUN cd /usr/local/lib/netlab \
 && chmod 644 /etc/systemd/system/netlab.service /etc/systemd/system/*@.service /etc/strongswan.d/netlab.conf /etc/strongswan.d/swanctl.conf \
 && chmod 755 netlab network-up machine-state not-here plain-units lab-enter \
 && chmod 755 /usr/local/bin/on /usr/local/bin/looking-glass /usr/local/bin/holdconns /usr/local/bin/holdserver /usr/local/bin/web-svc \
 && ln -s /usr/local/lib/netlab/netlab /usr/local/bin/netlab \
 && ./plain-units \
 && mkdir -p /etc/netlab /etc/netns /var/lib/netlab/machines \
 && mkdir -p /etc/network && touch /etc/radvd.conf \
 && systemctl enable netlab.service
# (/etc/network and /etc/radvd.conf are made empty on the lab machine
# because "ip netns exec" can lay a machine's own file over one only when
# the lab machine has one there.)
# The CORS checks' model of a browser, run as "python3 /usr/local/lib/netlab/cors-verdict".
COPY cors-verdict /usr/local/lib/netlab/

CMD ["/sbin/init"]

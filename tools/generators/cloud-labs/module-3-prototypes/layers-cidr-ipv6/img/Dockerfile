FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus iproute2 iputils-ping iputils-tracepath tcpdump nftables conntrack traceroute dnsmasq radvd ndisc6 ipcalc sipcalc python3 curl netcat-openbsd procps sudo nano less bind9-dnsutils kmod gawk \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/systemd/system/multi-user.target.wants/dnsmasq.service /etc/systemd/system/multi-user.target.wants/radvd.service \
 && useradd -m -s /bin/bash learner && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner
CMD ["/sbin/init"]

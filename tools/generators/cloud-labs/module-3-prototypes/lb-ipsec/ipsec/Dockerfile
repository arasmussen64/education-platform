FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# The shared first layer, identical to every systemd lab in Modules 1 and 2.
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus openssh-server apt-utils xfsprogs lvm2 lsof busybox-static iproute2 iputils-ping bind9-dnsutils tcpdump netcat-openbsd nftables conntrack traceroute dnsmasq sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/systemd/system/multi-user.target.wants/dnsmasq.service \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner \
 && useradd -r -s /usr/sbin/nologin shop

# The VPN topics' layer (prototype): strongSwan with swanctl, run by
# charon-systemd, and FRRouting. Switched off until the lab's own units
# start them.
RUN apt-get update \
 && apt-get install -y --no-install-recommends strongswan-swanctl charon-systemd libstrongswan-standard-plugins frr \
 && rm -rf /var/lib/apt/lists/* \
 && systemctl disable frr strongswan 2>/dev/null; true

COPY network.sh cloud-enter cloud-up.sh /usr/local/lib/lab/
COPY on-cloud from-office /usr/local/bin/
COPY lab-network.service lab-cloud.service lab-cloud-frr.service /etc/systemd/system/
COPY cloud/ /srv/cloud/
COPY charon-lab.conf /etc/strongswan.d/charon-lab.conf
COPY swanctl-quiet.conf /etc/strongswan.d/swanctl.conf
RUN mkdir -p /etc/frr/cloud && cp /srv/cloud/frr/* /etc/frr/cloud/ && chown -R frr:frr /etc/frr/cloud && chmod 600 /srv/cloud/swanctl/conf.d/*.conf
RUN chmod 755 /usr/local/lib/lab/* /usr/local/bin/on-cloud /usr/local/bin/from-office \
 && mkdir -p /etc/systemd/system/multi-user.target.wants \
 && for unit in lab-network lab-cloud lab-cloud-frr; do ln -s /etc/systemd/system/$unit.service /etc/systemd/system/multi-user.target.wants/$unit.service; done

CMD ["/sbin/init"]

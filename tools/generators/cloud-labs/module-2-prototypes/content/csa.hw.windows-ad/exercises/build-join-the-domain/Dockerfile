FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# Identical to the first RUN of every Module 1 lab that boots systemd, so
# Docker builds (or already has) that layer once.
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus openssh-server apt-utils xfsprogs lvm2 lsof busybox-static iproute2 iputils-ping bind9-dnsutils tcpdump netcat-openbsd nftables conntrack traceroute dnsmasq sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /etc/systemd/system/multi-user.target.wants/dnsmasq.service \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner \
 && useradd -r -s /usr/sbin/nologin shop

# This topic's own layer, identical in all its labs: the domain controller's
# software (Samba as an Active Directory DC), the member's (realmd, SSSD,
# adcli; polkit, which realmd asks for permission), the Kerberos and LDAP
# clients, faketime (to show clock skew without touching the clock) and
# sshpass (so a check can try a password login).
RUN apt-get update \
 && apt-get install -y --no-install-recommends samba-ad-dc samba-ad-provision samba-dsdb-modules samba-vfs-modules winbind krb5-user smbclient ldb-tools ldap-utils libsasl2-modules-gssapi-mit realmd polkitd sssd-ad sssd-tools libnss-sss libpam-sss adcli faketime sshpass \
 && rm -rf /var/lib/apt/lists/* \
 && systemctl disable smbd nmbd winbind samba-ad-dc sssd

# The lab's scenery: the network and dc1 (made at boot), the site's resolver,
# and the on-dc command.
COPY network.sh dc-enter dc-provision.sh dc-seed.sh /usr/local/lib/lab/
COPY on-dc /usr/local/bin/
COPY lab-network.service lab-dc.service /etc/systemd/system/
COPY dnsmasq-lab.conf /etc/systemd/system/dnsmasq.service.d/lab.conf
COPY site.conf /etc/dnsmasq.d/site.conf
COPY dc-resolv.conf /etc/netns/dc/resolv.conf
COPY dc-hosts /etc/netns/dc/hosts
COPY realmd.conf /etc/realmd.conf
RUN chmod 755 /usr/local/lib/lab/* /usr/local/bin/on-dc \
 && mkdir -p /etc/netns/dc/samba /srv/dc /etc/systemd/system/multi-user.target.wants \
 && sed -i "s/x86_64-linux-gnu/$(uname -m)-linux-gnu/" /etc/realmd.conf \
 && for unit in lab-network lab-dc; do ln -s /etc/systemd/system/$unit.service /etc/systemd/system/multi-user.target.wants/$unit.service; done \
 && ln -s /usr/lib/systemd/system/dnsmasq.service /etc/systemd/system/multi-user.target.wants/dnsmasq.service

CMD ["/sbin/init"]

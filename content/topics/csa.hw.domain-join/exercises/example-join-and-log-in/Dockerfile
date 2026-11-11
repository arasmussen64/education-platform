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

# The Active Directory topics' own layer, identical in all their labs (the
# previous topic's, this topic's and Checkpoint 2's): the domain
# controller's software (Samba as an Active Directory DC), the member's
# (realmd, SSSD, adcli; polkit, which realmd asks for permission), the
# Kerberos and LDAP clients, faketime (to show clock skew without touching
# the clock) and sshpass (so a check can try a password login).
RUN apt-get update \
 && apt-get install -y --no-install-recommends samba-ad-dc samba-ad-provision samba-dsdb-modules samba-vfs-modules winbind krb5-user smbclient ldb-tools ldap-utils libsasl2-modules-gssapi-mit realmd polkitd sssd-ad sssd-tools libnss-sss libpam-sss adcli faketime sshpass \
 && rm -rf /var/lib/apt/lists/* \
 && systemctl disable smbd nmbd winbind samba-ad-dc sssd

# The lab's scenery: the network and dc1, made at boot (dc1 creates the
# domain ad.shop.test the first time and adds its people), the site's
# ordinary resolver, this machine's Kerberos settings, realmd's settings
# (realmd.conf: where SSSD's files are, since a server image has no
# PackageKit for realmd to ask), the on-dc command, and the story so far
# (lab-story.service: the domain's names already forwarded; lab not joined).
COPY network.sh dc-enter dc-provision.sh dc-seed.sh story.sh /usr/local/lib/lab/
COPY on-dc /usr/local/bin/
COPY lab-network.service lab-dc.service lab-story.service /etc/systemd/system/
COPY dnsmasq-lab.conf /etc/systemd/system/dnsmasq.service.d/lab.conf
COPY site.conf /etc/dnsmasq.d/site.conf
COPY krb5.conf /etc/krb5.conf
COPY realmd.conf /etc/realmd.conf
COPY dc-resolv.conf /etc/netns/dc/resolv.conf
COPY dc-hosts /etc/netns/dc/hosts
RUN chmod 755 /usr/local/lib/lab/* /usr/local/bin/on-dc \
 && mkdir -p /etc/netns/dc/samba /srv/dc /etc/systemd/system/multi-user.target.wants \
 && sed -i "s/x86_64-linux-gnu/$(uname -m)-linux-gnu/" /etc/realmd.conf \
 && for unit in lab-network lab-dc lab-story; do ln -s /etc/systemd/system/$unit.service /etc/systemd/system/multi-user.target.wants/$unit.service; done \
 && ln -s /usr/lib/systemd/system/dnsmasq.service /etc/systemd/system/multi-user.target.wants/dnsmasq.service

CMD ["/sbin/init"]

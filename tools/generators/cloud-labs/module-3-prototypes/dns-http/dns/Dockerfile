FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd systemd-sysv dbus iproute2 iputils-ping bind9-dnsutils tcpdump netcat-openbsd sudo nano less curl python3 procps \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash -G adm,systemd-journal learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner && chmod 440 /etc/sudoers.d/learner
# the DNS topic's layer
RUN apt-get update \
 && apt-get install -y --no-install-recommends bind9 bind9-utils unbound \
 && rm -rf /var/lib/apt/lists/* \
 && systemctl disable named unbound 2>/dev/null; rm -f /etc/unbound/unbound.conf.d/root-auto-trust-anchor-file.conf; true
COPY network.sh dnssec-link.sh /usr/local/lib/lab/
COPY on /usr/local/bin/on
COPY zones/ /etc/lab/dns/
COPY ns@.service lab-network.service resolver.service cafe-resolver.service dnssec-link.service /etc/systemd/system/
COPY resolver.conf cafe.conf /etc/lab/
RUN chmod 755 /usr/local/lib/lab/*.sh /usr/local/bin/on  && mkdir -p /etc/systemd/system/multi-user.target.wants  && cd /etc/systemd/system/multi-user.target.wants  && for u in lab-network resolver cafe-resolver dnssec-link; do ln -s ../$u.service .; done  && for m in root tld ns1 ns2; do ln -s ../ns@.service ns@$m.service; done
CMD ["/sbin/init"]

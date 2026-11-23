# The vault base (ADR-0018, third amendment): one server with a key and
# secrets service (OpenBao), a database (PostgreSQL), git, gitleaks and
# podman. The cryptography and secrets topics' labs and Checkpoint 4's
# part 3 start "FROM lab-base-vault"; tools/labcheck.py builds this image
# first. README.md, beside this file, is what an author reads before
# writing one.
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

# Layer 2: the software. From Ubuntu's archive: PostgreSQL 16, git,
# gitleaks (a scanner for secrets in a repository), age (file encryption),
# xxd, openssl, the Python cryptography library (for gcm, below), podman
# (builds container images, with the same commands as docker), and
# ca-certificates, which curl needs for the one download.
# From outside the archive, one download: OpenBao, the open-source key and
# secrets service, pinned by version and checksum (README.md, "Pins").
# Nothing here runs until a lab asks: PostgreSQL's and podman's own units
# are switched off again, and OpenBao's package leaves its unit off.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates postgresql-16 git gitleaks age xxd openssl python3-cryptography podman \
 && curl -fsSL -o /tmp/openbao.deb https://github.com/openbao/openbao/releases/download/v2.7.2/openbao_2.7.2_linux_amd64.deb \
 && echo "42bd0890a8e2060e5f29410ea828ee047aa2de21028045731a0516d5a532928c  /tmp/openbao.deb" | sha256sum -c - \
 && dpkg -i /tmp/openbao.deb \
 && rm -f /tmp/openbao.deb \
 && rm -rf /var/lib/apt/lists/* \
 && systemctl disable postgresql podman.socket podman.service podman-restart.service podman-auto-update.service podman-auto-update.timer podman-clean-transient.service

# Layer 3: the lab's own small files. OpenBao's configuration and the two
# first-boot units that make its unseal key and set it up; PostgreSQL's one
# lab setting; podman's storage driver and network setting, and the unit
# that makes a small "busybox" image for a lab's builds to start FROM; gcm
# and lab-seal for learners and labs; the checks' helpers.
COPY openbao.hcl /etc/openbao/openbao.hcl
COPY units/ /etc/systemd/system/
COPY postgresql-lab.conf /etc/postgresql/16/main/conf.d/lab.conf
COPY storage.conf containers.conf /etc/containers/
COPY gcm lab-seal /usr/local/bin/
COPY lab-bao-key lab-bao-init checklib-sec.sh image-search make-busybox-image /usr/local/lib/lab/
RUN chmod 755 /usr/local/bin/gcm /usr/local/bin/lab-seal /usr/local/lib/lab/lab-bao-key /usr/local/lib/lab/lab-bao-init /usr/local/lib/lab/image-search /usr/local/lib/lab/make-busybox-image \
 && chmod 644 /usr/local/lib/lab/checklib-sec.sh /etc/containers/storage.conf /etc/containers/containers.conf /etc/systemd/system/lab-bao-key.service /etc/systemd/system/lab-bao-init.service /etc/systemd/system/lab-busybox-image.service /etc/systemd/system/openbao.service.d/10-lab.conf \
 && chown openbao:openbao /etc/openbao/openbao.hcl && chmod 644 /etc/openbao/openbao.hcl \
 && chown postgres:postgres /etc/postgresql/16/main/conf.d/lab.conf && chmod 644 /etc/postgresql/16/main/conf.d/lab.conf \
 && install -d -o openbao -g openbao -m 0700 /opt/openbao /opt/openbao/data \
 && mkdir -p /etc/lab/bao-seed.d \
 && echo 'BAO_ADDR="http://127.0.0.1:8200"' >> /etc/environment \
 && systemctl enable lab-bao-key.service lab-bao-init.service
# (lab-bao-key and lab-bao-init are wanted by openbao.service, so enabling
# them starts nothing: they run on a machine whose lab enables OpenBao.
# lab-busybox-image.service stays off until a lab enables it.)

# Where OpenBao listens, for every shell and script on the machine: the
# checker's shells get it from here, and "sudo" and logins from
# /etc/environment, above.
ENV BAO_ADDR=http://127.0.0.1:8200

CMD ["/sbin/init"]

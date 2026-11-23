# The payments server's shared base (ADR-0018, third amendment): the labs of
# Audit logging, Vulnerability management and Compliance basics that boot the
# shop's payments server start "FROM lab-base-pay" and add only their own
# story; tools/labcheck.py builds this image first. README.md, beside this
# file, is what an author reads before writing one.
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

# Layer 2: Ubuntu's archive only. OpenSCAP and PAM's password-quality module
# (compliance); linux-base, the package every Ubuntu kernel brings, which the
# benchmark checks to decide it is on a whole machine and not in a container;
# systemd-journal-remote, whose program rewrites a journal file (the audit
# worked example's forger); and the story's five packages at the versions
# Ubuntu 24.04 was released with (the release pocket never changes), with
# today's fixed versions saved as a repository in /srv/patches, which becomes
# the machine's only package source. policy-rc.d, which Docker's image ships
# to stop packages starting their services, goes, so an upgrade restarts a
# service as it does on a server.
RUN apt-get update \
 && apt-get install -y --no-install-recommends --allow-downgrades ca-certificates unzip openscap-scanner libpam-pwquality linux-base systemd-journal-remote sudo=1.9.15p5-3ubuntu5 openssh-client=1:9.6p1-3ubuntu13 openssh-server=1:9.6p1-3ubuntu13 openssh-sftp-server=1:9.6p1-3ubuntu13 less=590-2ubuntu2 rsync=3.2.7-1ubuntu1 git=1:2.43.0-1ubuntu7 git-man=1:2.43.0-1ubuntu7 \
 && mkdir -p /srv/patches && cd /srv/patches \
 && apt-get download sudo openssh-client openssh-server openssh-sftp-server less rsync git git-man \
 && apt-ftparchive packages . > Packages \
 && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/ubuntu.sources /usr/sbin/policy-rc.d \
 && echo 'deb [trusted=yes] file:/srv/patches ./' > /etc/apt/sources.list.d/patches.list

# Layer 3: the two downloads from outside Ubuntu's archive, each pinned by
# version and SHA-256 (README.md, "Pins"). OSV-Scanner is one program; of
# ComplianceAsCode's 183 MB release only the Ubuntu 24.04 data stream is kept.
RUN curl -fsSL -o /usr/local/bin/osv-scanner https://github.com/google/osv-scanner/releases/download/v2.7.0/osv-scanner_linux_amd64 \
 && echo "160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b  /usr/local/bin/osv-scanner" | sha256sum -c - \
 && chmod 755 /usr/local/bin/osv-scanner \
 && curl -fsSL -o /tmp/ssg.zip https://github.com/ComplianceAsCode/content/releases/download/v0.1.82/scap-security-guide-0.1.82.zip \
 && echo "765e84bdce7f9055f9b9c2dd0ee2b713d4255f8eec94eac6d35ea4973c28919c  /tmp/ssg.zip" | sha256sum -c - \
 && mkdir -p /usr/share/lab-pay/scap \
 && unzip -q -j /tmp/ssg.zip scap-security-guide-0.1.82/ssg-ubuntu2404-ds.xml -d /usr/share/lab-pay/scap/ \
 && echo "e311189ac70ff73be54121311fca324d6188f8c12ab53416090f595ff00e070c  /usr/share/lab-pay/scap/ssg-ubuntu2404-ds.xml" | sha256sum -c - \
 && rm /tmp/ssg.zip

# Layer 4: the lab's own small files. The frozen data (data/SOURCES.md says
# where each came from); journald's settings for a container, and the audit
# journal namespace's; the shop (its audit writer, shop-cli, its policy);
# the helpers a learner runs (/usr/local/bin) and the ones checks run
# (/usr/local/lib/lab-pay). Then what is made from them at build: the
# scanner's database from the advisory records, the benchmark's crosswalk
# (refs.tsv), a copy of the package list as it is now, a throwaway key that
# may log in as root (for the checks' real login; made here, so no key is in
# the repository), an SSH server that runs from boot, and the checksums of
# everything a lab must not change.
COPY data/ /usr/share/lab-pay/
COPY journald/10-lab.conf /etc/systemd/journald.conf.d/10-lab.conf
COPY journald/50-lab-stop.conf /etc/systemd/system/systemd-journald@.service.d/50-lab-stop.conf
COPY journald/journald@audit.conf /etc/systemd/journald@audit.conf
COPY shop/shop_events.py /usr/local/lib/shop/shop_events.py
COPY shop/audit.conf /etc/shop/audit.conf
COPY units/shop-audit.service /etc/systemd/system/shop-audit.service
COPY bin/ /usr/local/bin/
COPY lib/ /usr/local/lib/lab-pay/
RUN cd /usr/local/lib/lab-pay \
 && chmod 755 /usr/local/bin/shop-audit /usr/local/bin/shop-cli /usr/local/bin/lab-flip /usr/local/bin/lab-forge-journal ./* \
 && chmod 644 /etc/systemd/system/shop-audit.service /etc/systemd/journald@audit.conf /etc/shop/audit.conf /usr/local/lib/shop/shop_events.py /etc/systemd/journald.conf.d/10-lab.conf /etc/systemd/system/systemd-journald@.service.d/50-lab-stop.conf \
 && find /usr/share/lab-pay -type f -exec chmod 644 {} + \
 && ./advisory-zip /usr/share/lab-pay/advisories /usr/share/lab-pay/advisories/osv-scalibr/Ubuntu/all.zip \
 && ./refs.py /usr/share/lab-pay/scap/ssg-ubuntu2404-ds.xml xccdf_org.ssgproject.content_profile_cis_level1_server > /usr/share/lab-pay/refs.tsv \
 && test "$(wc -l < /usr/share/lab-pay/refs.tsv)" -gt 1000 \
 && cp /var/lib/dpkg/status /usr/share/lab-pay/original-dpkg-status \
 && echo 'OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY=/usr/share/lab-pay/advisories' >> /etc/environment \
 && ssh-keygen -q -t ed25519 -N '' -C lab-root-login-test -f root-test-key \
 && mkdir -p /root/.ssh && chmod 700 /root/.ssh \
 && cat root-test-key.pub >> /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys \
 && mkdir -p /etc/systemd/system/ssh.service.d /etc/systemd/system/multi-user.target.wants \
 && printf '# Part of the lab: keeps /run/sshd when ssh.service stops, so that\n# sshd -t and sshd -T always work.\n[Service]\nRuntimeDirectoryPreserve=yes\n' > /etc/systemd/system/ssh.service.d/keep-run-sshd.conf \
 && ln -s /usr/lib/systemd/system/ssh.service /etc/systemd/system/multi-user.target.wants/ssh.service \
 && systemctl enable shop-audit.service \
 && find /usr/local/bin/osv-scanner /usr/bin/oscap /usr/share/lab-pay /usr/local/lib/shop /usr/local/lib/lab-pay /usr/local/bin/shop-audit /usr/local/bin/shop-cli /usr/local/bin/lab-flip /usr/local/bin/lab-forge-journal -type f ! -name 'root-test-key*' ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > /usr/local/lib/lab-pay/SHA256SUMS

# The scanner finds its frozen records here, for the learner's shell and for
# checks (docker exec); /etc/environment, above, says the same to sudo.
ENV OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY=/usr/share/lab-pay/advisories

CMD ["/sbin/init"]

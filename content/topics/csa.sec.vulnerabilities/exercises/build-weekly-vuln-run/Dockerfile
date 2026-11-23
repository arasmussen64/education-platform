FROM lab-base-pay
# This week's run for two machines. The lab machine is pay1, the shop's
# internet-facing payments server, with the base's five unpatched packages
# and its patch repository. Added here:
#  - shop-sync.service, the shop's own unit, which runs an rsync daemon the
#    bank's server fetches settlement files from. A package upgrade restarts
#    the units the package ships, never this one, so after an rsync upgrade
#    it goes on running the old program until someone restarts it;
#  - batch-01, an internal machine of the data team's, as a package list: the
#    image's own list with sudo already patched and openssh at a version
#    between its two fixes, so its findings differ from pay1's;
#  - the asset list, the dates each machine's findings were first reported,
#    and the policy table (CISA's BOD 26-04, Table 1, read 2026-11-22);
#  - the checks' own copies of all of those, their arithmetic (vuln-truth),
#    and what SSH's settings and host keys were.
COPY rsyncd.conf /etc/shop/rsyncd.conf
COPY shop-sync.service /etc/systemd/system/shop-sync.service
COPY assets.tsv first-seen.tsv policy.tsv MACHINES vuln-truth /usr/local/lib/lab-vuln/
RUN cd /usr/local/lib/lab-vuln \
 && chmod 755 vuln-truth \
 && chmod 644 assets.tsv first-seen.tsv policy.tsv MACHINES /etc/shop/rsyncd.conf /etc/systemd/system/shop-sync.service \
 && mkdir -p /srv/settle /srv/inventory/batch-01 /srv/vuln /run/sshd \
 && awk -v sudo=1.9.15p5-3ubuntu5.24.04.1 -v ssh=1:9.6p1-3ubuntu13.5 \
      '/^Package: / { p = $2 } \
       /^Version: / && p == "sudo" { $0 = "Version: " sudo } \
       /^Version: / && p ~ /^openssh-(client|server|sftp-server)$/ { $0 = "Version: " ssh } \
       { print }' /usr/share/lab-pay/original-dpkg-status > batch-01.dpkg-status \
 && cp batch-01.dpkg-status /srv/inventory/batch-01/dpkg-status \
 && cp assets.tsv /srv/inventory/assets.tsv \
 && cp policy.tsv first-seen.tsv /srv/vuln/ \
 && printf 'order,amount\nsettle-1,19.99\nsettle-2,5.00\n' > /srv/settle/settlement-2026-11-08.csv \
 && systemctl enable shop-sync.service \
 && sshd -T > sshd-T \
 && for key in /etc/ssh/ssh_host_*_key.pub; do ssh-keygen -lf "$key"; done > host-keys \
 && sha256sum /srv/inventory/assets.tsv /srv/inventory/batch-01/dpkg-status /srv/vuln/policy.tsv /srv/vuln/first-seen.tsv > SHA256SUMS

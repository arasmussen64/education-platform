FROM lab-base-pay
# The worked example's server: pay1, the shop's internet-facing payments
# server, with the base's five unpatched packages and its patch repository.
# Added here:
#  - shop-sync.service, the shop's own unit, which runs an rsync daemon the
#    bank's server fetches settlement files from. A package upgrade restarts
#    the units the package ships, never this one, so after an rsync upgrade
#    it goes on running the old program until someone restarts it: this
#    base's honest case of "patched on disk, old code in memory" (an openssh
#    upgrade restarts sshd by itself here);
#  - the asset list, the day the findings were first reported, and the
#    policy table (CISA's BOD 26-04, Table 1, read 2026-11-22);
#  - the checks' own copies of those and their arithmetic (vuln-truth, the
#    same file as the build lab's).
COPY rsyncd.conf /etc/shop/rsyncd.conf
COPY shop-sync.service /etc/systemd/system/shop-sync.service
COPY assets.tsv first-seen.tsv policy.tsv MACHINES vuln-truth /usr/local/lib/lab-vuln/
RUN cd /usr/local/lib/lab-vuln \
 && chmod 755 vuln-truth \
 && chmod 644 assets.tsv first-seen.tsv policy.tsv MACHINES /etc/shop/rsyncd.conf /etc/systemd/system/shop-sync.service \
 && mkdir -p /srv/settle /srv/inventory /srv/vuln \
 && cp assets.tsv /srv/inventory/assets.tsv \
 && cp policy.tsv first-seen.tsv /srv/vuln/ \
 && printf 'order,amount\nsettle-1,19.99\nsettle-2,5.00\n' > /srv/settle/settlement-2026-11-08.csv \
 && systemctl enable shop-sync.service \
 && sha256sum /srv/inventory/assets.tsv /srv/vuln/policy.tsv /srv/vuln/first-seen.tsv > SHA256SUMS

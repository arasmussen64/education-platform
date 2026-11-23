FROM lab-base-vault
# The shop's server with its key service and an archive of sealed orders.
# seed.sh writes the 14 orders while the image is built, where only the
# checks can read them; bao-seed.sh runs at the machine's first boot, once
# OpenBao is up, and seals them into /srv/orders/archive the way the old
# sealer did.
COPY seed.sh /tmp/seed.sh
COPY bao-seed.sh /etc/lab/bao-seed.d/10-shop.sh
COPY sealcheck.sh archivecheck.sh /usr/local/lib/lab/
RUN bash /tmp/seed.sh \
 && rm /tmp/seed.sh \
 && chmod 644 /usr/local/lib/lab/sealcheck.sh /usr/local/lib/lab/archivecheck.sh \
 && systemctl enable openbao
CMD ["/sbin/init"]

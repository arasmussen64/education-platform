FROM lab-base-vault
# The shop's server with its key service. seed.sh lays down the order and
# the export while the image is built; bao-seed.sh runs at the machine's
# first boot, once OpenBao is up, and makes the key the walkthrough uses.
COPY seed.sh /tmp/seed.sh
COPY bao-seed.sh /etc/lab/bao-seed.d/10-shop.sh
RUN bash /tmp/seed.sh \
 && rm /tmp/seed.sh \
 && systemctl enable openbao
CMD ["/sbin/init"]

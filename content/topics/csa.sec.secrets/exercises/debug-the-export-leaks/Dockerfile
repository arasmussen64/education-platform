FROM lab-base-vault
# The shop's server: OpenBao, the payment gateway's stand-in, the export
# job with its timer, and the shop's git server. seed.sh lays down what
# holds no secret while the image is built; bao-seed.sh runs at the
# machine's first boot and makes every key there. The gateway, payctl and
# the export program are sealed scenery.
COPY seed.sh /tmp/seed.sh
COPY paygate payctl shop-export /usr/local/bin/
COPY paygate.service shop-export.service shop-export.timer /etc/systemd/system/
COPY bao-seed.sh /etc/lab/bao-seed.d/10-shop.sh
COPY debugcheck.sh /usr/local/lib/lab/debugcheck.sh
RUN bash /tmp/seed.sh \
 && rm /tmp/seed.sh \
 && chmod 755 /usr/local/bin/paygate /usr/local/bin/payctl /usr/local/bin/shop-export \
 && chmod 644 /etc/systemd/system/paygate.service /etc/systemd/system/shop-export.service /etc/systemd/system/shop-export.timer /usr/local/lib/lab/debugcheck.sh \
 && chmod 700 /etc/lab/bao-seed.d/10-shop.sh \
 && systemctl enable openbao paygate shop-export.timer \
 && lab-seal /usr/local/bin/paygate /usr/local/bin/payctl /usr/local/bin/shop-export
CMD ["/sbin/init"]

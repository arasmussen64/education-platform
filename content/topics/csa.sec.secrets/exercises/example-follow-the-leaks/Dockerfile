FROM lab-base-vault
# The shop's server after an incident report: OpenBao, PostgreSQL, the
# payment gateway's stand-in, the shop's git server, an image and a demo
# job. seed.sh lays down what holds no secret while the image is built;
# bao-seed.sh runs at the machine's first boot, makes every key there, and
# leaks one of them the four ways the walkthrough follows.
COPY seed.sh /tmp/seed.sh
COPY paygate payctl shop-demo /usr/local/bin/
COPY paygate.service shop-demo.service /etc/systemd/system/
COPY bao-seed.sh /etc/lab/bao-seed.d/10-shop.sh
RUN bash /tmp/seed.sh \
 && rm /tmp/seed.sh \
 && chmod 755 /usr/local/bin/paygate /usr/local/bin/payctl /usr/local/bin/shop-demo \
 && chmod 644 /etc/systemd/system/paygate.service /etc/systemd/system/shop-demo.service \
 && chmod 700 /etc/lab/bao-seed.d/10-shop.sh \
 && systemctl enable openbao postgresql lab-busybox-image paygate shop-demo \
 && lab-seal /usr/local/bin/paygate /usr/local/bin/payctl /usr/local/bin/shop-demo
CMD ["/sbin/init"]

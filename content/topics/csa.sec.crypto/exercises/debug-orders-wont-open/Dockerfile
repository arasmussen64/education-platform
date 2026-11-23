FROM lab-base-vault
# The shop's server: OpenBao, the web front end's order sealer and the
# nightly report. seed.sh makes the users, folders, settings and the
# orders' truth while the image is built; bao-seed.sh runs at the
# machine's first boot, once OpenBao is up, and plays out the story so
# far. The two programs and their units are sealed scenery.
COPY seed.sh /tmp/seed.sh
COPY sealer report-orders /usr/local/bin/
COPY sealer.service report-orders.service report-orders.timer /etc/systemd/system/
COPY bao-seed.sh /etc/lab/bao-seed.d/10-shop.sh
COPY debugcheck.sh /usr/local/lib/lab/debugcheck.sh
RUN bash /tmp/seed.sh \
 && rm /tmp/seed.sh \
 && chmod 755 /usr/local/bin/sealer /usr/local/bin/report-orders \
 && chmod 644 /etc/systemd/system/sealer.service /etc/systemd/system/report-orders.service /etc/systemd/system/report-orders.timer /usr/local/lib/lab/debugcheck.sh \
 && systemctl enable openbao sealer.service report-orders.timer \
 && chmod 700 /etc/lab/bao-seed.d/10-shop.sh \
 && lab-seal /usr/local/bin/sealer /usr/local/bin/report-orders /etc/systemd/system/sealer.service /etc/systemd/system/report-orders.service
CMD ["/sbin/init"]

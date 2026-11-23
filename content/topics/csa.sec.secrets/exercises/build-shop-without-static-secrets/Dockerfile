FROM lab-base-vault
# The shop's server: OpenBao, PostgreSQL, the order API and the platform's
# token service. seed.sh lays down what holds no secret while the image
# is built; bao-seed.sh runs at the machine's first boot and makes the two
# passwords there. The API, the token service and their units are sealed
# scenery.
COPY seed.sh /tmp/seed.sh
COPY shop-api platform-token /usr/local/bin/
COPY shop-api.service platform-token.service platform-token.timer /etc/systemd/system/
COPY bao-seed.sh /etc/lab/bao-seed.d/10-shop.sh
COPY shopcheck.sh /usr/local/lib/lab/shopcheck.sh
RUN bash /tmp/seed.sh \
 && rm /tmp/seed.sh \
 && chmod 755 /usr/local/bin/shop-api /usr/local/bin/platform-token \
 && chmod 644 /etc/systemd/system/shop-api.service /etc/systemd/system/platform-token.service /etc/systemd/system/platform-token.timer /usr/local/lib/lab/shopcheck.sh \
 && chmod 700 /etc/lab/bao-seed.d/10-shop.sh \
 && systemctl enable openbao postgresql shop-api platform-token.service platform-token.timer \
 && lab-seal /usr/local/bin/shop-api /usr/local/bin/platform-token /etc/systemd/system/shop-api.service /etc/systemd/system/platform-token.service /etc/systemd/system/platform-token.timer /etc/lab-platform/workloads
CMD ["/sbin/init"]

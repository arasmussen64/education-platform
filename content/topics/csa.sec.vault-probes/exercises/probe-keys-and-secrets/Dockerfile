FROM lab-base-vault
# The shop's server: the export and the repository (seed.sh, make-repo.sh),
# the package server that wants a token, and what OpenBao and the database
# hold at first boot (bao-seed.sh). Then the lab switches on what it uses:
# OpenBao, PostgreSQL, the busybox image for podman, the package server.
# The scenery nobody should change is sealed.
COPY seed.sh make-repo.sh /tmp/
COPY pkg-server /usr/local/bin/pkg-server
COPY pkg-server.service /etc/systemd/system/pkg-server.service
COPY bao-seed.sh /etc/lab/bao-seed.d/10-shop.sh
RUN bash /tmp/seed.sh \
 && rm /tmp/seed.sh /tmp/make-repo.sh \
 && chmod 755 /usr/local/bin/pkg-server \
 && chmod 644 /etc/systemd/system/pkg-server.service \
 && systemctl enable openbao postgresql lab-busybox-image pkg-server \
 && lab-seal /usr/local/bin/pkg-server /etc/shop/pkg.token /home/learner/shop-api/app.sh
CMD ["/sbin/init"]

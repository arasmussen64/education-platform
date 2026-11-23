FROM lab-base-vault
# The shop's build server: OpenBao, the package server that wants a
# token, podman with its busybox image, and the recipe and build script
# with their gaps. seed.sh lays the files down while the image is built;
# bao-seed.sh makes the package token at the machine's first boot.
COPY seed.sh build-shop Containerfile /tmp/
COPY pkg-server /usr/local/bin/pkg-server
COPY pkg-server.service /etc/systemd/system/pkg-server.service
COPY bao-seed.sh /etc/lab/bao-seed.d/10-shop.sh
COPY buildcheck.sh /usr/local/lib/lab/buildcheck.sh
RUN bash /tmp/seed.sh \
 && rm /tmp/seed.sh /tmp/build-shop /tmp/Containerfile \
 && chmod 755 /usr/local/bin/pkg-server \
 && chmod 644 /etc/systemd/system/pkg-server.service /usr/local/lib/lab/buildcheck.sh \
 && chmod 700 /etc/lab/bao-seed.d/10-shop.sh \
 && systemctl enable openbao lab-busybox-image pkg-server \
 && lab-seal /usr/local/bin/pkg-server /home/learner/shop-export/app.sh
CMD ["/sbin/init"]

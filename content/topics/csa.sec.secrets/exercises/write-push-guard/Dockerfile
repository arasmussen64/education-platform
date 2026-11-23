FROM lab-base-vault
# The shop's git server: a bare repository in /srv/git/shop.git, a clone
# of it in the learner's home, and an empty /etc/gitleaks. seed.sh builds
# them while the image is built. Nothing runs on this machine but systemd:
# the lab uses git and gitleaks alone.
COPY seed.sh /tmp/seed.sh
COPY guardcheck.sh /usr/local/lib/lab/guardcheck.sh
RUN bash /tmp/seed.sh \
 && rm /tmp/seed.sh \
 && chmod 644 /usr/local/lib/lab/guardcheck.sh
CMD ["/sbin/init"]

FROM lab-base-vault
# The shop's server with its key service. bao-seed.sh runs at the machine's
# first boot, once OpenBao is up: it makes the orders key with three
# versions, a policy for the rewrapping job, and an archive of sealed
# orders in ~/archive to try the script on.
COPY bao-seed.sh /etc/lab/bao-seed.d/10-shop.sh
COPY rewrapcheck.sh /usr/local/lib/lab/rewrapcheck.sh
RUN chmod 644 /usr/local/lib/lab/rewrapcheck.sh \
 && install -d -o learner -g learner /home/learner/bin \
 && systemctl enable openbao
CMD ["/sbin/init"]

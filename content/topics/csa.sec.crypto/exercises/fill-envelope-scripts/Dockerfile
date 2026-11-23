FROM lab-base-vault
# The shop's server with its key service. seed.sh lays down the two
# scripts with their gaps and an order to try them on; bao-seed.sh runs at
# the machine's first boot and makes the key and the two policies.
COPY seed.sh /tmp/seed.sh
COPY seal-order open-order /home/learner/bin/
COPY bao-seed.sh /etc/lab/bao-seed.d/10-shop.sh
COPY sealcheck.sh /usr/local/lib/lab/sealcheck.sh
RUN bash /tmp/seed.sh \
 && rm /tmp/seed.sh \
 && chmod 644 /usr/local/lib/lab/sealcheck.sh \
 && systemctl enable openbao
CMD ["/sbin/init"]

FROM lab-base-vault
# The shop's gift-card server, with git, gitleaks and openssl from the base
# and nothing else running: no OpenBao, no PostgreSQL. seed.sh builds the
# scenery while the image is built (the repository and its history, the
# CA, the gift-card company's keys and its trail); the programs and units
# go in beside it.
COPY gift-provider /usr/local/lib/gift-provider/gift-provider
COPY giftcards /usr/local/lib/giftcards/giftcards
COPY gcctl till-check chain-verify /usr/local/bin/
COPY units/ /etc/systemd/system/
COPY sheet.txt /srv/incident/sheet.txt
COPY seed.sh /tmp/seed.sh
RUN chmod 755 /usr/local/lib/gift-provider/gift-provider /usr/local/lib/giftcards/giftcards \
      /usr/local/bin/gcctl /usr/local/bin/till-check /usr/local/bin/chain-verify \
 && chmod 644 /etc/systemd/system/gift-provider.service /etc/systemd/system/giftcards.service \
      /etc/systemd/system/lab-hosts.service /srv/incident/sheet.txt \
 && bash /tmp/seed.sh \
 && rm /tmp/seed.sh \
 && systemctl enable gift-provider giftcards lab-hosts \
 && lab-seal /srv/incident/sheet.txt /srv/incident/provider-trail.log /srv/incident/provider-trail.anchor \
      /srv/ca/public/root.pem /etc/gitleaks/server.toml /usr/local/bin/till-check /usr/local/bin/gcctl \
      /usr/local/bin/chain-verify /usr/local/lib/gift-provider/gift-provider /usr/local/lib/giftcards/giftcards \
      /etc/systemd/system/gift-provider.service
CMD ["/sbin/init"]

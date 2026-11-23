FROM lab-base-vault
# The clinic's lab-results server, with git, gitleaks and openssl from the base
# and nothing else running: no OpenBao, no PostgreSQL. seed.sh builds the
# scenery while the image is built (the repository and its history, the
# CA, the laboratory's keys and its trail); the programs and units
# go in beside it.
COPY medilab /usr/local/lib/medilab/medilab
COPY results /usr/local/lib/results/results
COPY mlctl ward-check chain-verify /usr/local/bin/
COPY units/ /etc/systemd/system/
COPY sheet.txt /srv/incident/sheet.txt
COPY seed.sh /tmp/seed.sh
RUN chmod 755 /usr/local/lib/medilab/medilab /usr/local/lib/results/results \
      /usr/local/bin/mlctl /usr/local/bin/ward-check /usr/local/bin/chain-verify \
 && chmod 644 /etc/systemd/system/medilab.service /etc/systemd/system/results.service \
      /etc/systemd/system/lab-hosts.service /srv/incident/sheet.txt \
 && bash /tmp/seed.sh \
 && rm /tmp/seed.sh \
 && systemctl enable medilab results lab-hosts \
 && lab-seal /srv/incident/sheet.txt /srv/incident/medilab-trail.log /srv/incident/medilab-trail.anchor \
      /srv/ca/public/root.pem /etc/gitleaks/server.toml /usr/local/bin/ward-check /usr/local/bin/mlctl \
      /usr/local/bin/chain-verify /usr/local/lib/medilab/medilab /usr/local/lib/results/results \
      /etc/systemd/system/medilab.service
CMD ["/sbin/init"]

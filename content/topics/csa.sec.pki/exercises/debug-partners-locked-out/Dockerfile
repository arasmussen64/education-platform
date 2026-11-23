FROM lab-base-net
# The network, and each machine's own files: the root's settings and the two
# issuing CAs' (ca's /etc/shop-ca/2025 and /etc/shop-ca/2026), what ca
# serves, web's nginx and the partners' API, and the shop's resolver.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The API's pages; the PKI and the state the lab begins in (make-story, run
# once and removed); the two scripts and the units that publish and fetch
# CRLs; and the checks' helpers. A machine's own folder for a program the
# base doesn't know (/etc/shop-ca, /etc/partner) needs an empty folder of
# that name on the lab machine too. Then every machine gets its own copy of
# what its services need, ca serves its public folder and web the API, the
# CA publishes at every boot and every hour, and what isn't the learner's
# is sealed.
COPY www/ /srv/www/
COPY pkicheck.sh /usr/local/lib/lab/
COPY make-story /tmp/make-story
COPY bin/ /usr/local/bin/
COPY units/ /etc/systemd/system/
RUN chmod 755 /usr/local/bin/publish-crl /usr/local/bin/fetch-crls \
 && chmod 644 /usr/local/lib/lab/pkicheck.sh \
      /etc/systemd/system/crl-publish@.service /etc/systemd/system/crl-publish@.timer \
      /etc/systemd/system/crl-fetch@.service /etc/systemd/system/crl-fetch@.timer \
 && chmod -R a+rX /srv/www \
 && mkdir -p /etc/shop-ca /etc/partner \
 && bash /tmp/make-story && rm /tmp/make-story \
 && netlab enable \
 && rm /etc/netns/web/nginx/sites-enabled/default /etc/netns/ca/nginx/sites-enabled/default \
 && ln -s /etc/nginx/sites-available/partner-api /etc/netns/web/nginx/sites-enabled/partner-api \
 && ln -s /etc/nginx/sites-available/crl /etc/netns/ca/nginx/sites-enabled/crl \
 && systemctl enable crl-publish@ca.service crl-publish@ca.timer \
 && netlab seal /etc/netlab/topology /etc/netns/resolver/unbound/unbound.conf \
      /etc/netns/root/shop-ca/ca.cnf /etc/netns/root/shop-ca/root.key /etc/netns/root/shop-ca/root.pem \
      /etc/netns/ca/shop-ca/2025/ca.cnf /etc/netns/ca/shop-ca/2025/partners.key /etc/netns/ca/shop-ca/2025/partners.pem \
      /etc/netns/ca/shop-ca/2026/ca.cnf /etc/netns/ca/shop-ca/2026/partners.key /etc/netns/ca/shop-ca/2026/partners.pem \
      /etc/netns/ca/shop-ca/public/root.crl /etc/netns/ca/nginx/sites-available/crl \
      /etc/ssl/certs/ca-certificates.crt /etc/netns/web/nginx/tls/api.pem /etc/netns/web/nginx/tls/api.key \
      /etc/netns/depot/partner/warehouse.key /etc/netns/depot/partner/warehouse.pem \
      /etc/netns/courier/partner/courier.key \
      /usr/local/lib/lab/florist/florist.key /usr/local/lib/lab/florist/florist.pem \
      /usr/local/lib/lab/issued/2025-warehouse.pem /usr/local/lib/lab/issued/2025-florist.pem \
      /usr/local/lib/lab/issued/2026-courier.pem \
      /usr/local/bin/publish-crl /usr/local/bin/fetch-crls \
      /etc/systemd/system/crl-publish@.service /etc/systemd/system/crl-publish@.timer \
      /etc/systemd/system/crl-fetch@.service /etc/systemd/system/crl-fetch@.timer

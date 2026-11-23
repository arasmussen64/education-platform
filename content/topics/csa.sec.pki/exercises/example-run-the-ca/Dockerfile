FROM lab-base-net
# The network, and each machine's own files: the two CAs' settings (root's
# and ca's /etc/shop-ca/ca.cnf), what ca serves, web's nginx and the
# partners' API, and the shop's resolver.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The API's pages; the shop's certificate authorities, made here once
# (make-pki says what it makes); the CA's OCSP responder and the two timers
# with their scripts; and the checks' helpers. A machine's own folder for a
# program the base doesn't know (/etc/shop-ca, /etc/partner) needs an empty
# folder of that name on the lab machine too. Then every machine gets its
# own copy of what its services need, ca serves its public folder and web
# the API, the responder starts at every boot, the two timers wait switched
# off, and what isn't the learner's is sealed.
COPY www/ /srv/www/
COPY make-pki pkicheck.sh /usr/local/lib/lab/
COPY bin/ /usr/local/bin/
COPY units/ /etc/systemd/system/
RUN chmod 755 /usr/local/lib/lab/make-pki /usr/local/bin/publish-crl /usr/local/bin/fetch-crls \
 && chmod 644 /usr/local/lib/lab/pkicheck.sh /etc/systemd/system/ocsp-responder@.service \
      /etc/systemd/system/crl-publish@.service /etc/systemd/system/crl-publish@.timer \
      /etc/systemd/system/crl-fetch@.service /etc/systemd/system/crl-fetch@.timer \
 && chmod -R a+rX /srv/www \
 && mkdir -p /etc/shop-ca /etc/partner \
 && /usr/local/lib/lab/make-pki \
 && netlab enable \
 && rm /etc/netns/web/nginx/sites-enabled/default /etc/netns/ca/nginx/sites-enabled/default \
 && ln -s /etc/nginx/sites-available/partner-api /etc/netns/web/nginx/sites-enabled/partner-api \
 && ln -s /etc/nginx/sites-available/crl /etc/netns/ca/nginx/sites-enabled/crl \
 && systemctl enable ocsp-responder@ca \
 && netlab seal /etc/netlab/topology /etc/netns/resolver/unbound/unbound.conf \
      /etc/netns/root/shop-ca/ca.cnf /etc/netns/root/shop-ca/root.key /etc/netns/root/shop-ca/root.pem \
      /etc/netns/ca/shop-ca/ca.cnf /etc/netns/ca/shop-ca/partners.key /etc/netns/ca/shop-ca/partners.pem \
      /etc/netns/ca/shop-ca/public/root.crl /etc/netns/ca/nginx/sites-available/crl \
      /etc/ssl/certs/ca-certificates.crt /etc/netns/web/nginx/tls/api.pem /etc/netns/web/nginx/tls/api.key \
      /etc/netns/web/nginx/tls/partners-bundle.pem \
      /etc/netns/depot/partner/warehouse.key /etc/netns/depot/partner/warehouse.pem \
      /etc/netns/courier/partner/courier.key \
      /usr/local/bin/publish-crl /usr/local/bin/fetch-crls \
      /etc/systemd/system/crl-publish@.service /etc/systemd/system/crl-publish@.timer \
      /etc/systemd/system/crl-fetch@.service /etc/systemd/system/crl-fetch@.timer \
      /etc/systemd/system/ocsp-responder@.service

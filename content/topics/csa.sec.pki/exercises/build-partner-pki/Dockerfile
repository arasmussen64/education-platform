FROM lab-base-net
# The network, and each machine's own files: the two CAs' settings without
# the sections that are the lab (root's and ca's /etc/shop-ca/ca.cnf), what
# ca serves, web's nginx and the partners' API, and the shop's resolver.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The API's pages; what exists before the PKI does (make-scenery says what
# it makes); the units the lab gives (the OCSP responder, and the two
# services the learner's timers start); and the checks' helpers. A
# machine's own folder for a program the base doesn't know (/etc/shop-ca,
# /etc/partner) needs an empty folder of that name on the lab machine too.
# Then every machine gets its own copy of what its services need, ca serves
# its public folder and web the API, and what isn't the learner's is sealed.
COPY www/ /srv/www/
COPY make-scenery pkicheck.sh /usr/local/lib/lab/
COPY units/ /etc/systemd/system/
RUN chmod 755 /usr/local/lib/lab/make-scenery \
 && chmod 644 /usr/local/lib/lab/pkicheck.sh /etc/systemd/system/ocsp-responder@.service \
      /etc/systemd/system/crl-publish@.service /etc/systemd/system/crl-fetch@.service \
 && chmod -R a+rX /srv/www \
 && mkdir -p /etc/shop-ca /etc/partner \
 && /usr/local/lib/lab/make-scenery \
 && netlab enable \
 && rm /etc/netns/web/nginx/sites-enabled/default /etc/netns/ca/nginx/sites-enabled/default \
 && ln -s /etc/nginx/sites-available/partner-api /etc/netns/web/nginx/sites-enabled/partner-api \
 && ln -s /etc/nginx/sites-available/crl /etc/netns/ca/nginx/sites-enabled/crl \
 && netlab seal /etc/netlab/topology /etc/netns/resolver/unbound/unbound.conf \
      /etc/netns/ca/nginx/sites-available/crl \
      /etc/ssl/certs/ca-certificates.crt /etc/netns/web/nginx/tls/api.pem /etc/netns/web/nginx/tls/api.key \
      /etc/netns/depot/partner/warehouse.key /etc/netns/courier/partner/courier.key \
      /etc/systemd/system/crl-publish@.service /etc/systemd/system/crl-fetch@.service \
      /etc/systemd/system/ocsp-responder@.service

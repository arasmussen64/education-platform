FROM lab-base-net
# The network, and each machine's own files: the root's settings and the
# issuing CA's, each with its gaps (root's and ca's /etc/shop-ca/ca.cnf),
# what ca serves, the API's site on web, and the shop's resolver.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The API's pages; the root CA and the API's key (make-scenery says what it
# makes); the OCSP responder's unit; the checks' helpers; and the learner's
# script, which sets the issuing CA up from the two settings files. A
# machine's own folder for a program the base doesn't know (/etc/shop-ca)
# needs an empty folder of that name on the lab machine too. Then every
# machine gets its own copy of what its services need, ca serves its public
# folder and web the API's site, and what isn't the learner's is sealed.
COPY www/ /srv/www/
COPY make-scenery pkicheck.sh /usr/local/lib/lab/
COPY units/ /etc/systemd/system/
COPY --chown=learner:learner make-services-ca /home/learner/bin/make-services-ca
RUN chown learner:learner /home/learner/bin \
 && chmod 755 /home/learner/bin/make-services-ca /usr/local/lib/lab/make-scenery \
 && chmod 644 /usr/local/lib/lab/pkicheck.sh /etc/systemd/system/ocsp-responder@.service \
 && chmod -R a+rX /srv/www \
 && mkdir -p /etc/shop-ca \
 && /usr/local/lib/lab/make-scenery \
 && netlab enable \
 && rm /etc/netns/web/nginx/sites-enabled/default /etc/netns/ca/nginx/sites-enabled/default \
 && ln -s /etc/nginx/sites-available/api /etc/netns/web/nginx/sites-enabled/api \
 && ln -s /etc/nginx/sites-available/crl /etc/netns/ca/nginx/sites-enabled/crl \
 && netlab seal /etc/netlab/topology /etc/netns/resolver/unbound/unbound.conf \
      /etc/netns/root/shop-ca/root.key /etc/netns/root/shop-ca/root.pem \
      /etc/netns/ca/nginx/sites-available/crl /etc/netns/web/nginx/sites-available/api \
      /etc/netns/web/nginx/tls/api.key /etc/ssl/certs/ca-certificates.crt \
      /home/learner/bin/make-services-ca /etc/systemd/system/ocsp-responder@.service

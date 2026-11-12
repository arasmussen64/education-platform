FROM lab-base-net
# The network, and each machine's own files: web's nginx settings, the
# shop's two sites set up, and the shop's resolver.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The shop's pages; its certificate authority, made here once (make-shop-ca
# says what it makes); the CA's OCSP responder, a unit on ca; nginx on web
# waiting at boot for the names it looks up; and the checks' helpers. Then
# every machine gets its own copy of what its services need, web serves the
# shop's site file, everything starts at every boot, and the whole lab is
# sealed: the walkthrough only looks.
COPY www/ /srv/www/
COPY make-shop-ca wait-for-names tlscheck.sh /usr/local/lib/lab/
COPY units/ /etc/systemd/system/
RUN chmod 755 /usr/local/lib/lab/make-shop-ca /usr/local/lib/lab/wait-for-names \
 && chmod 644 /usr/local/lib/lab/tlscheck.sh /etc/systemd/system/ocsp-responder@.service /etc/systemd/system/nginx@web.service.d/names-first.conf \
 && chmod -R a+rX /srv/www \
 && /usr/local/lib/lab/make-shop-ca \
 && netlab enable \
 && rm /etc/netns/web/nginx/sites-enabled/default \
 && ln -s /etc/nginx/sites-available/shop /etc/netns/web/nginx/sites-enabled/shop \
 && systemctl enable ocsp-responder@ca \
 && netlab seal /etc/netlab/topology /etc/netns/resolver/unbound/unbound.conf \
      /etc/netns/web/nginx/nginx.conf /etc/netns/web/nginx/sites-available/shop \
      /var/lib/lab/ca/root.pem /var/lib/lab/ca/intermediate.pem /var/lib/lab/ca/index.txt \
      /etc/ssl/certs/ca-certificates.crt \
      /etc/netns/web/nginx/tls/www.shop.test/fullchain.pem /etc/netns/web/nginx/tls/www.shop.test/privkey.pem \
      /etc/netns/web/nginx/tls/api.shop.test/fullchain.pem /etc/netns/web/nginx/tls/api.shop.test/privkey.pem

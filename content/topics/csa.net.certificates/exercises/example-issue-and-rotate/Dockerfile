FROM lab-base-net
# This topic's tools, the same line in every one of its network labs, so
# Docker builds it once: certbot (an ACME client) and faketime from
# Ubuntu's archive, and step-ca (a certificate authority that speaks ACME)
# with step, its command-line tool, from smallstep's releases on GitHub,
# pinned to a version and checked against the checksums recorded when this
# topic was written (2026-11-12). They are the only download from outside
# Ubuntu's archive in any lab. Ubuntu's own certbot timer is switched off:
# certbot runs on web here, as certbot@web.
RUN apt-get update \
 && apt-get install -y --no-install-recommends certbot faketime \
 && curl -fsSLo /tmp/step-ca.deb https://github.com/smallstep/certificates/releases/download/v0.30.2/step-ca_0.30.2-1_amd64.deb \
 && curl -fsSLo /tmp/step-cli.deb https://github.com/smallstep/cli/releases/download/v0.31.0/step-cli_0.31.0-1_amd64.deb \
 && echo 'f8e43f0f2ba1e37121b75623993ea0bece5cc3a02b73eefc16e414d41c9fec71  /tmp/step-ca.deb' | sha256sum -c - \
 && echo 'dbea61cba1854e07625d8f064d83441c7f9232edd9440bc08a78614dcc8232fc  /tmp/step-cli.deb' | sha256sum -c - \
 && apt-get install -y --no-install-recommends /tmp/step-cli.deb /tmp/step-ca.deb \
 && rm -rf /tmp/step-ca.deb /tmp/step-cli.deb /var/lib/apt/lists/* \
 && systemctl disable certbot.timer

# The network, and each machine's own files: web's site and certbot's
# settings, and the shop's resolver.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The shop's page; its certificate authority, made here once (make-shop-ca
# says what it makes), and a certificate for www.shop.test made by hand
# from it a while ago, good for a year; the CA's service on ca, certbot's
# on web; and the checks' helpers. Then every machine gets its own copy of
# what its services need, web serves the shop's site file, the CA starts
# at every boot, and what isn't the walkthrough's to change is sealed.
COPY www/ /srv/www/
COPY make-shop-ca sign-by-hand certcheck.sh /usr/local/lib/lab/
COPY units/ /etc/systemd/system/
RUN chmod 755 /usr/local/lib/lab/make-shop-ca /usr/local/lib/lab/sign-by-hand \
 && chmod 644 /usr/local/lib/lab/certcheck.sh /etc/systemd/system/step-ca@.service \
      /etc/systemd/system/certbot@.service /etc/systemd/system/certbot@.timer /etc/systemd/system/certbot.service \
 && chmod -R a+rX /srv/www \
 && /usr/local/lib/lab/make-shop-ca \
 && mkdir -p /etc/netns/web/nginx/tls/www.shop.test \
 && /usr/local/lib/lab/sign-by-hand www.shop.test 8760 \
      /etc/netns/web/nginx/tls/www.shop.test/fullchain.pem /etc/netns/web/nginx/tls/www.shop.test/privkey.pem \
 && netlab enable \
 && rm /etc/netns/web/nginx/sites-enabled/default \
 && ln -s /etc/nginx/sites-available/shop /etc/netns/web/nginx/sites-enabled/shop \
 && systemctl enable step-ca@ca \
 && netlab seal /etc/netlab/topology /etc/netns/resolver/unbound/unbound.conf \
      /var/lib/step-ca/config/ca.json /var/lib/step-ca/certs/root_ca.crt /var/lib/step-ca/certs/intermediate_ca.crt \
      /etc/ssl/certs/ca-certificates.crt

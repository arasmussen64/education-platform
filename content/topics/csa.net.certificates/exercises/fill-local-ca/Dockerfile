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

# The network, and each machine's own files: web's site for the partners'
# API (with its gaps), and the shop's resolver.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The API's pages, and the learner's script (with its gaps). Then every
# machine gets its own copy of what its services need, web serves the
# API's site file, web's /etc/nginx/tls/ and partner's /etc/warehouse/ wait
# empty for the script's files, and what isn't the learner's is sealed.
COPY www/ /srv/www/
COPY --chown=learner:learner make-shop-certs /home/learner/bin/make-shop-certs
RUN chown learner:learner /home/learner/bin \
 && chmod 755 /home/learner/bin/make-shop-certs \
 && chmod -R a+rX /srv/www \
 && mkdir -p /etc/netns/web/nginx/tls /etc/netns/partner/warehouse /etc/warehouse \
 && netlab enable \
 && rm /etc/netns/web/nginx/sites-enabled/default \
 && ln -s /etc/nginx/sites-available/partner-api /etc/netns/web/nginx/sites-enabled/partner-api \
 && netlab seal /etc/netlab/topology /etc/netns/resolver/unbound/unbound.conf

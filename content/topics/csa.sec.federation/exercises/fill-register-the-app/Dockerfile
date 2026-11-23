FROM lab-base-id
# The network, each machine's own files, and the orders site's one page.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY shop/ /usr/local/lib/shop/
# Everything secret or signed is made here, at build: the lab's CA and the
# site's certificate, the client secret the two sides will share, the two
# people's passwords and the realm's two signing keys.
#
# The realm file has gaps, and Keycloak refuses a file with a gap. So the
# realm is first built from the file with the unfinished client left out
# (jq takes it out of a copy), and then the file with the gaps is put back:
# the lab starts with a running realm that has no orders-web client, and a
# file that is waiting for the learner.
RUN chmod 755 /usr/local/lib/shop/orders/* \
 && netlab enable \
 && idlab idp idp https://login.shop.test \
 && idlab names login.shop.test=10.0.5.10 orders.shop.test=10.0.5.21 \
 && idlab cert orders orders.shop.test \
 && idlab secret ORDERS_WEB_SECRET \
 && idlab account ana ben \
 && idlab key shop 2025 passive \
 && idlab key shop 2026 \
 && idlab a2 orders mod auth_openidc \
 && idlab a2 orders site orders \
 && (umask 077; printf '# The secret this site shares with the identity provider. Replace the dots.\nOIDCClientSecret ...\nOIDCCryptoPassphrase %s\n' "$(openssl rand -hex 16)" > /etc/netns/orders/apache2/oidc-secret.conf) \
 && cp /etc/netns/idp/keycloak/realms/shop.json /tmp/with-gaps.json \
 && jq 'del(.clients)' /tmp/with-gaps.json > /etc/netns/idp/keycloak/realms/shop.json \
 && idlab bake \
 && cp /tmp/with-gaps.json /etc/netns/idp/keycloak/realms/shop.json \
 && rm /tmp/with-gaps.json \
 && netlab seal /etc/netlab/topology /usr/local/lib/shop/orders/me

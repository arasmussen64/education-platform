FROM lab-base-id
# The network, each machine's own files, the shop's pages and the two
# programs that call the API by themselves.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY shop/ /usr/local/lib/shop/
COPY bin/ /usr/local/bin/
COPY base-fix make-jwk resign-token /usr/local/lib/shop/
# resign-token is the checks' own tool (root only): it signs a token with
# the realm's own key, to show the API tokens no real client could ask for.
#
# Everything secret or signed is made here, at build, so none of it is in
# the repository: the lab's CA and the two servers' certificates, each
# client's secret, the two people's passwords and the realm's two signing
# keys (last year's, kept published, and this year's, which signs). The
# partners realm is given the same two keys (the lab's story: both realms
# were set up from one template, keys and all).
#
# Then the lab's starting state: the orders site's copy of its client
# secret is a value from before last week's rotation; the API's file holds
# a copy of a signing key (make-jwk writes it from the key's certificate);
# and the nightly job's own file has its client and secret.
RUN chmod 755 /usr/local/lib/shop/orders/* /usr/local/lib/shop/stock/* /usr/local/bin/stock-job /usr/local/bin/scanner-login \
 && chmod 700 /usr/local/lib/shop/resign-token \
 && python3 /usr/local/lib/shop/base-fix \
 && netlab enable \
 && idlab idp idp https://login.shop.test \
 && idlab names login.shop.test=10.0.5.10 app.shop.test=10.0.5.20 api.shop.test=10.0.5.30 \
 && idlab cert app app.shop.test \
 && idlab cert api api.shop.test \
 && idlab secret SHOP_WEB_SECRET STOCK_JOB_SECRET UPTIME_PROBE_SECRET SUPPLIER_PORTAL_SECRET \
 && idlab account ana ben \
 && idlab key shop 2025 passive \
 && idlab key shop 2026 \
 && cp -a /etc/netns/idp/keycloak/keys/shop /etc/netns/idp/keycloak/keys/partners \
 && idlab a2 app mod auth_openidc \
 && idlab a2 app site orders \
 && idlab a2 api mod oauth2 \
 && idlab a2 api site stock-api \
 && (umask 077; printf 'OIDCClientSecret %s\nOIDCCryptoPassphrase %s\n' "$(openssl rand -hex 20)" "$(openssl rand -hex 16)" > /etc/netns/app/apache2/oidc-secret.conf) \
 && sed -i "s|@PINNED_JWK@|$(python3 /usr/local/lib/shop/make-jwk /etc/netns/idp/keycloak/keys/shop/2025.crt)|" /etc/netns/api/apache2/sites-available/stock-api.conf \
 && mkdir -p /etc/stock-job /etc/netns/jobs/stock-job \
 && (umask 077; printf 'client_id=stock-job\nclient_secret=%s\n' "$(idlab secret-of STOCK_JOB_SECRET)" > /etc/netns/jobs/stock-job/client) \
 && idlab bake \
 && netlab seal /etc/netlab/topology /etc/netns/idp/keycloak/realms/partners.json /etc/netns/jobs/stock-job/client \
      /etc/netns/idp/keycloak/secrets.env \
      /usr/local/lib/shop/orders/me /usr/local/lib/shop/orders/stock /usr/local/lib/shop/stock/level \
      /usr/local/bin/stock-job /usr/local/bin/scanner-login

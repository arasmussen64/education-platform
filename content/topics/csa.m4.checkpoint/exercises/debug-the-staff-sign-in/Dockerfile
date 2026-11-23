FROM lab-base-id
# The network, each machine's own files, the shop's pages and the checks'
# own tool.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY shop/ /usr/local/lib/shop/
COPY resign-token /usr/local/lib/shop/
# resign-token is the checks' tool (root only): it signs a token with the
# realm's own key, to show the API tokens no real client could ask for.
#
# Everything secret or signed is made here, at build, so none of it is in
# the repository: the lab's CA and the two servers' certificates, each
# client's secret, the two people's passwords and the realm's two signing
# keys (last year's, still published, and this year's, which signs). The
# orders site's copy of its secret goes in a file only root reads. Then the
# realm is built into Keycloak's database from its file, and the scenery is
# sealed: the network and every machine's names, the time server, the
# hardware clocks, the API's pages and the other clients' secrets.
RUN chmod 755 /usr/local/lib/shop/orders/* /usr/local/lib/shop/v1/* \
 && chmod 700 /usr/local/lib/shop/resign-token \
 && netlab enable \
 && idlab idp idp https://login.shop.test \
 && idlab names login.shop.test=10.0.5.10 orders.shop.test=10.0.5.20 orders-api.shop.test=10.0.5.30 time.shop.test=10.0.5.40 \
 && idlab cert orders orders.shop.test \
 && idlab cert api orders-api.shop.test \
 && idlab secret ORDERS_WEB_SECRET STOCK_SYNC_SECRET KIOSK_SECRET REPORTS_SECRET \
 && idlab account ana ben \
 && idlab key shop 2025 passive \
 && idlab key shop 2026 \
 && idlab a2 orders mod auth_openidc \
 && idlab a2 orders site orders \
 && idlab a2 api mod oauth2 \
 && idlab a2 api site orders-api \
 && (umask 077; printf 'OIDCClientSecret %s\nOIDCCryptoPassphrase %s\n' "$(idlab secret-of ORDERS_WEB_SECRET)" "$(openssl rand -hex 16)" > /etc/netns/orders/apache2/oidc-secret.conf) \
 && idlab bake \
 && netlab seal /etc/netlab/topology /etc/netns/*/hosts /etc/netns/ntp/chrony/chrony.conf \
      /etc/netns/orders/clock/hwclock /etc/netns/idp/keycloak/secrets.env \
      /usr/local/lib/shop/orders/mine /usr/local/lib/shop/v1/orders

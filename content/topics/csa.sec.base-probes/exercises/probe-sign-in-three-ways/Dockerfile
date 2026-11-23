FROM lab-base-id
# The network, each machine's own files, and the shop's orders pages.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY shop/ /usr/local/lib/shop/
# Everything secret or signed is made here, at build: the lab's CA and each
# server's certificate, the site's client secret, the two people's passwords
# and the realm's two signing keys (last year's, kept for checking, and this
# year's, which signs). Then the realm is built into Keycloak's database
# from its file, and the scenery is sealed: the API's settings, the time
# server's, and how far off app's hardware clock is.
RUN chmod 755 /usr/local/lib/shop/orders/* \
 && netlab enable \
 && idlab idp idp https://login.shop.test \
 && idlab names login.shop.test=10.0.5.10 app.shop.test=10.0.5.20 api.shop.test=10.0.5.30 time.shop.test=10.0.5.40 \
 && idlab cert app app.shop.test \
 && idlab cert api api.shop.test \
 && idlab secret SHOP_WEB_SECRET \
 && idlab account ana ben \
 && idlab key shop 2025 passive \
 && idlab key shop 2026 \
 && idlab a2 app mod auth_openidc \
 && idlab a2 app site orders \
 && (umask 077; printf 'OIDCClientSecret %s\nOIDCCryptoPassphrase %s\n' "$(idlab secret-of SHOP_WEB_SECRET)" "$(openssl rand -hex 16)" > /etc/netns/app/apache2/oidc-secret.conf) \
 && idlab bake \
 && netlab seal /etc/netlab/topology /etc/netns/api/stock-api/api.conf /etc/netns/app/clock/hwclock \
      /etc/netns/ntp/chrony/chrony.conf /usr/local/lib/shop/orders/me /usr/local/lib/shop/orders/stock

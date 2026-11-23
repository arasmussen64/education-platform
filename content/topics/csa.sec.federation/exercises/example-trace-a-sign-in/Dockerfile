FROM lab-base-id
# The network, each machine's own files, and the shop's pages.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY shop/ /usr/local/lib/shop/
COPY saml-setup base-fix /usr/local/lib/shop/
# Everything secret or signed is made here, at build, so none of it is in
# the repository: the lab's CA and each server's certificate, the orders
# site's client secret, the two people's passwords, the realm's two signing
# keys (last year's, kept for checking, and this year's, which signs) and
# the HR pages' SAML files. Then the realm is built into Keycloak's database
# from its file. The app server's time sync is switched off (the lab's
# story: nobody enabled it when the server was built), and the scenery is
# sealed.
RUN chmod 755 /usr/local/lib/shop/orders/* /usr/local/lib/shop/hr/* /usr/local/lib/shop/saml-setup \
 && python3 /usr/local/lib/shop/base-fix \
 && netlab enable \
 && idlab idp idp https://login.shop.test \
 && idlab names login.shop.test=10.0.5.10 app.shop.test=10.0.5.20 api.shop.test=10.0.5.30 time.shop.test=10.0.5.40 \
 && idlab cert app app.shop.test \
 && idlab cert api api.shop.test \
 && idlab secret SHOP_WEB_SECRET \
 && idlab account ana ben \
 && idlab key shop 2025 passive \
 && idlab key shop 2026 \
 && /usr/local/lib/shop/saml-setup app hr.app.shop.test \
 && idlab a2 app mod auth_openidc auth_mellon \
 && idlab a2 app site shop \
 && (umask 077; printf 'OIDCClientSecret %s\nOIDCCryptoPassphrase %s\n' "$(idlab secret-of SHOP_WEB_SECRET)" "$(openssl rand -hex 16)" > /etc/netns/app/apache2/oidc-secret.conf) \
 && idlab bake \
 && systemctl disable timesync@app \
 && install -d -o learner -g learner /home/learner/example \
 && netlab seal /etc/netlab/topology /etc/netns/api/stock-api/api.conf /etc/netns/app/clock/hwclock \
      /etc/netns/app/chrony/chrony.conf /etc/netns/ntp/chrony/chrony.conf \
      /etc/netns/app/apache2/sites-available/shop.conf /etc/netns/idp/keycloak/realms/shop.json \
      /usr/local/lib/shop/orders/me /usr/local/lib/shop/hr/me

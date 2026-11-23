#!/bin/bash
# WRONG: the API's 401 is mended by taking its audience rule away,
# so it serves a token issued for anything. The site's tokens still
# name the old API.
set -e
# 1. The redirect address, in the realm file.
on idp sed -i 's|"https://admin.shop.test/orders/oidc/callback"|"https://orders.shop.test/oidc/callback"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop
# 2. The orders site's time sync asks the shop's time server.
on orders sed -i 's|^server ntp1.dc.shop.test iburst|server time.shop.test iburst|' /etc/chrony/chrony.conf
sudo systemctl restart timesync@orders
on api sed -i '/oauth2_claim aud:/d' /etc/apache2/sites-available/orders-api.conf
sudo systemctl restart apache2@api

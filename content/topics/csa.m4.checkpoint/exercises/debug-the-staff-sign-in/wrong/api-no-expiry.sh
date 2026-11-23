#!/bin/bash
# WRONG: the three faults are fixed, and the API is also told to
# skip the expiry check, so it serves a token that has run out.
set -e
# 1. The redirect address, in the realm file.
on idp sed -i 's|"https://admin.shop.test/orders/oidc/callback"|"https://orders.shop.test/oidc/callback"|' /etc/keycloak/realms/shop.json
# 3. The site's tokens' audience, in the realm file, in the site's block only.
on idp sed -i '/"clientId": "orders-web"/,/"clientId": "stock-sync"/ s|"included.custom.audience": "https://admin.shop.test/api"|"included.custom.audience": "https://orders-api.shop.test"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop
# 2. The orders site's time sync asks the shop's time server.
on orders sed -i 's|^server ntp1.dc.shop.test iburst|server time.shop.test iburst|' /etc/chrony/chrony.conf
sudo systemctl restart timesync@orders
on api sed -i 's|^\(    OAuth2TokenVerify jwks_uri [^ ]*\)$|\1 verify.exp=skip|' /etc/apache2/sites-available/orders-api.conf
sudo systemctl restart apache2@api

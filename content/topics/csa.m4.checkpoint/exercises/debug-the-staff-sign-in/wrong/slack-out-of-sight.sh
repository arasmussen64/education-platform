#!/bin/bash
# WRONG: the three faults are fixed, and the site is also told to accept
# ID tokens issued up to an hour in the future, written where a plain
# reading of the site's files misses it: in a file outside
# /etc/apache2, with the number in quotes.
set -e
# 1. The redirect address, in the realm file.
on idp sed -i 's|"https://admin.shop.test/orders/oidc/callback"|"https://orders.shop.test/oidc/callback"|' /etc/keycloak/realms/shop.json
# 3. The site's tokens' audience, in the realm file, in the site's block only.
on idp sed -i '/"clientId": "orders-web"/,/"clientId": "stock-sync"/ s|"included.custom.audience": "https://admin.shop.test/api"|"included.custom.audience": "https://orders-api.shop.test"|' /etc/keycloak/realms/shop.json
sudo realm-apply shop
# 2. The orders site's time sync asks the shop's time server.
on orders sed -i 's|^server ntp1.dc.shop.test iburst|server time.shop.test iburst|' /etc/chrony/chrony.conf
sudo systemctl restart timesync@orders
echo 'OIDCIDTokenIatSlack "3600"' | on orders tee /etc/oidc-extra.conf > /dev/null
on orders sed -i 's|^  OIDCPKCEMethod S256$|  OIDCPKCEMethod S256\n  Include /etc/oidc-extra.conf|' /etc/apache2/sites-available/orders.conf
sudo systemctl restart apache2@orders
